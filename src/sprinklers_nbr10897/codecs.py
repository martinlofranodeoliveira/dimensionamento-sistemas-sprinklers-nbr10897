"""Codificadores e decodificadores canônicos JSON para sprinklers NBR 10897:2020.

Garante conformidade RFC 8259:
- Rejeição estrita de BOM (\ufeff / \xef\xbb\xbf);
- Rejeição de chaves duplicadas no parsing;
- Rejeição de números de ponto flutuante IEEE-754 no parsing de entrada;
- Limite estrito de profundidade recursiva (máx 32);
- Serialização determinística com ordenação alfabética de chaves e indentação.
"""

from __future__ import annotations

from fractions import Fraction
import json
from typing import Any

from sprinklers_nbr10897.models import (
    BicoSprinkler,
    ConexoesTrecho,
    InstalacaoSprinklers,
    ResultadoDimensionamentoSprinklers,
    ResultadoTrecho,
    TrechoRede,
)

PROFUNDIDADE_MAXIMA_JSON = 32


def parse_fracao_ou_int(val: Any, campo: str) -> Fraction:
    """Converte int, str fracionária ('41/10') ou str decimal ('4.1') em Fraction exata.

    Rejeita terminantemente float nativo.
    """
    if isinstance(val, float):
        raise TypeError(
            f"Valor de ponto flutuante float proibido no campo '{campo}'. "
            f"Forneça inteiro ou string exata (ex: '41/10' ou '4.1')."
        )
    if isinstance(val, int):
        return Fraction(val, 1)
    if isinstance(val, str):
        val_limpo = val.strip()
        if not val_limpo:
            raise ValueError(f"Campo '{campo}' não pode ser string vazia.")
        try:
            return Fraction(val_limpo)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"Valor numérico inválido '{val}' no campo '{campo}': {exc}") from exc
    raise TypeError(
        f"Tipo inválido para '{campo}': {type(val).__name__}. Esperado int ou str."
    )


def _verificar_profundidade(obj: Any, nivel: int = 1) -> None:
    if nivel > PROFUNDIDADE_MAXIMA_JSON:
        raise ValueError(
            f"Profundidade de aninhamento JSON ({nivel}) excede o limite máximo permitido ({PROFUNDIDADE_MAXIMA_JSON})."
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, nivel + 1)
    elif isinstance(obj, list):
        for item in obj:
            _verificar_profundidade(item, nivel + 1)


def _pares_sem_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada detectada no JSON: '{chave}'.")
        resultado[chave] = valor
    return resultado


def decodificar_instalacao_json(texto: str | bytes) -> InstalacaoSprinklers:
    """Decodifica JSON para InstalacaoSprinklers com validações rigorosas."""
    if isinstance(texto, bytes):
        if texto.startswith(b"\xef\xbb\xbf"):
            raise ValueError("BOM UTF-8 proibido no payload JSON.")
        texto_str = texto.decode("utf-8")
    else:
        if texto.startswith("\ufeff"):
            raise ValueError("BOM UTF-8 proibido no payload JSON.")
        texto_str = texto

    dados = json.loads(
        texto_str,
        object_pairs_hook=_pares_sem_duplicadas,
        parse_float=lambda s: (_ for _ in ()).throw(
            TypeError(f"Float '{s}' proibido. Utilize string fracionária ou decimal exata.")
        ),
    )

    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise TypeError("Payload JSON de instalação de sprinklers deve ser um objeto dicionário.")

    projeto = str(dados.get("projeto", "")).strip()
    classe_risco = str(dados.get("classe_risco", "")).strip()
    area_compartimento_m2 = parse_fracao_ou_int(dados.get("area_compartimento_m2"), "area_compartimento_m2")

    bico_raw = dados.get("bico")
    if not isinstance(bico_raw, dict):
        raise ValueError("Configuração 'bico' deve ser um objeto JSON.")

    modelo_fator_k = str(bico_raw.get("modelo_fator_k", "")).strip()
    espacamento_s_m = parse_fracao_ou_int(bico_raw.get("espacamento_s_m"), "espacamento_s_m")
    espacamento_l_m = parse_fracao_ou_int(bico_raw.get("espacamento_l_m"), "espacamento_l_m")

    bico = BicoSprinkler(
        modelo_fator_k=modelo_fator_k,
        espacamento_s_m=espacamento_s_m,
        espacamento_l_m=espacamento_l_m,
    )

    trechos_raw = dados.get("trechos")
    if not isinstance(trechos_raw, list):
        raise ValueError("Lista de 'trechos' deve ser um array JSON.")

    lista_trechos: list[TrechoRede] = []
    for idx, t in enumerate(trechos_raw):
        if not isinstance(t, dict):
            raise ValueError(f"Trecho índice {idx} deve ser um objeto JSON.")

        identificador = str(t.get("identificador", "")).strip()
        tubo_id = str(t.get("tubo_id", "")).strip()
        comp_real_m = parse_fracao_ou_int(t.get("comprimento_real_m"), f"trechos[{idx}].comprimento_real_m")
        desnivel_m = parse_fracao_ou_int(t.get("desnivel_geometrico_m", 0), f"trechos[{idx}].desnivel_geometrico_m")
        tem_vga = bool(t.get("tem_vga", False))

        conexoes_raw = t.get("conexoes", {})
        if not isinstance(conexoes_raw, dict):
            raise ValueError(f"Conexões do trecho '{identificador}' devem ser um objeto.")

        conexoes = ConexoesTrecho(
            joelho_90=int(conexoes_raw.get("joelho_90", 0)),
            te_passagem_direta=int(conexoes_raw.get("te_passagem_direta", 0)),
            te_saida_lateral=int(conexoes_raw.get("te_saida_lateral", 0)),
            valvula_gaveta=int(conexoes_raw.get("valvula_gaveta", 0)),
            valvula_retencao=int(conexoes_raw.get("valvula_retencao", 0)),
        )

        lista_trechos.append(
            TrechoRede(
                identificador=identificador,
                tubo_id=tubo_id,
                comprimento_real_m=comp_real_m,
                desnivel_geometrico_m=desnivel_m,
                conexoes=conexoes,
                tem_vga=tem_vga,
            )
        )

    margem_desbal = parse_fracao_ou_int(dados.get("margem_desbalanceamento_pct", "15"), "margem_desbalanceamento_pct")
    rendimento = parse_fracao_ou_int(dados.get("rendimento_bomba", "65/100"), "rendimento_bomba")

    return InstalacaoSprinklers(
        projeto=projeto,
        classe_risco=classe_risco,
        area_compartimento_m2=area_compartimento_m2,
        bico=bico,
        trechos=tuple(lista_trechos),
        margem_desbalanceamento_pct=margem_desbal,
        rendimento_bomba=rendimento,
    )


def instalacao_para_dict(inst: InstalacaoSprinklers) -> dict[str, Any]:
    """Converte InstalacaoSprinklers para dicionário JSON-serializável canônico."""
    return {
        "projeto": inst.projeto,
        "classe_risco": inst.classe_risco,
        "area_compartimento_m2": str(inst.area_compartimento_m2),
        "margem_desbalanceamento_pct": str(inst.margem_desbalanceamento_pct),
        "rendimento_bomba": str(inst.rendimento_bomba),
        "bico": {
            "modelo_fator_k": inst.bico.modelo_fator_k,
            "espacamento_s_m": str(inst.bico.espacamento_s_m),
            "espacamento_l_m": str(inst.bico.espacamento_l_m),
            "area_cobertura_m2": str(inst.bico.area_cobertura_m2),
        },
        "trechos": [
            {
                "identificador": t.identificador,
                "tubo_id": t.tubo_id,
                "comprimento_real_m": str(t.comprimento_real_m),
                "desnivel_geometrico_m": str(t.desnivel_geometrico_m),
                "tem_vga": t.tem_vga,
                "conexoes": {
                    "joelho_90": t.conexoes.joelho_90,
                    "te_passagem_direta": t.conexoes.te_passagem_direta,
                    "te_saida_lateral": t.conexoes.te_saida_lateral,
                    "valvula_gaveta": t.conexoes.valvula_gaveta,
                    "valvula_retencao": t.conexoes.valvula_retencao,
                },
            }
            for t in inst.trechos
        ],
    }


def resultado_para_dict(res: ResultadoDimensionamentoSprinklers) -> dict[str, Any]:
    """Converte ResultadoDimensionamentoSprinklers para dicionário canônico."""
    return {
        "projeto": res.projeto,
        "classe_risco": res.classe_risco,
        "nome_classe_risco": res.nome_classe_risco,
        "densidade_adotada_mm_min": str(res.densidade_adotada_mm_min),
        "area_operacao_adotada_m2": str(res.area_operacao_adotada_m2),
        "area_por_bico_m2": str(res.area_por_bico_m2),
        "vazao_bico_critico_l_min": str(res.vazao_bico_critico_l_min),
        "pressao_minima_bico_mca": str(res.pressao_minima_bico_mca),
        "fator_k": res.fator_k,
        "numero_bicos_operacao": res.numero_bicos_operacao,
        "vazao_bicos_l_min": str(res.vazao_bicos_l_min),
        "vazao_sprinklers_desbalanceada_l_min": str(res.vazao_sprinklers_desbalanceada_l_min),
        "vazao_hidrantes_adicionais_l_min": str(res.vazao_hidrantes_adicionais_l_min),
        "vazao_total_sistema_l_min": str(res.vazao_total_sistema_l_min),
        "tempo_minimo_rti_min": res.tempo_minimo_rti_min,
        "volume_rti_m3": str(res.volume_rti_m3),
        "perda_carga_total_tubulacao_mca": str(res.perda_carga_total_tubulacao_mca),
        "desnivel_geometrico_total_m": str(res.desnivel_geometrico_total_m),
        "altura_manometrica_total_mca": str(res.altura_manometrica_total_mca),
        "potencia_bomba_cv": str(res.potencia_bomba_cv),
        "potencia_comercial_bomba_cv": res.potencia_comercial_bomba_cv,
        "atende_norma": res.atende_norma,
        "observacoes": list(res.observacoes),
        "trechos": [
            {
                "identificador": t.identificador,
                "tubo_id": t.tubo_id,
                "dn_pol": t.dn_pol,
                "diametro_interno_mm": str(t.diametro_interno_mm),
                "vazao_l_min": str(t.vazao_l_min),
                "velocidade_m_s": str(t.velocidade_m_s),
                "comprimento_real_m": str(t.comprimento_real_m),
                "comprimento_equivalente_m": str(t.comprimento_equivalente_m),
                "comprimento_total_m": str(t.comprimento_total_m),
                "perda_unitaria_mca_m": str(t.perda_unitaria_mca_m),
                "perda_carga_mca": str(t.perda_carga_mca),
                "desnivel_m": str(t.desnivel_m),
            }
            for t in res.trechos
        ],
    }


def codificar_resultado_json(res: ResultadoDimensionamentoSprinklers) -> str:
    """Serializa ResultadoDimensionamentoSprinklers em JSON RFC 8259 formatado."""
    dados = resultado_para_dict(res)
    return json.dumps(dados, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
