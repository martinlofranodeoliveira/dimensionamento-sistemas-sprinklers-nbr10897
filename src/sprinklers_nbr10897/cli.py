"""Interface de linha de comando (CLI) em pt-BR para NBR 10897:2020.

Comandos:
- calcular: processa arquivo JSON de instalação de sprinklers e gera saídas;
- catalogo: exibe tabelas normativas de riscos, fatores K e tubulações de aço;
- gerar-exemplo: cria modelo JSON representativo pronto para uso.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sprinklers_nbr10897.calculator import calcular_sprinklers_nbr10897
from sprinklers_nbr10897.codecs import (
    codificar_resultado_json,
    decodificar_instalacao_json,
    instalacao_para_dict,
)
from sprinklers_nbr10897.constants import (
    CLASSES_RISCO_OCUPACAO,
    FATORES_K_SPRINKLERS,
    TUBOS_ACO_SPRINKLERS,
)
from sprinklers_nbr10897.exporters import (
    criar_pacote_zip_deterministico,
    formatar_fracao_decimal,
    gerar_csv_trechos,
    gerar_relatorio_texto,
)
from sprinklers_nbr10897.models import (
    BicoSprinkler,
    ConexoesTrecho,
    InstalacaoSprinklers,
    TrechoRede,
)
from sprinklers_nbr10897.svg_generator import gerar_painel_svg
from fractions import Fraction


def comando_catalogo(args: argparse.Namespace) -> int:
    """Exibe classes de risco, bicos e tubulações da NBR 10897."""
    print("=" * 80)
    print("  CATÁLOGO NORMATIVO ABNT NBR 10897:2020 - SPRINKLERS")
    print("=" * 80)

    print("\n1. CLASSES DE RISCO DE OCUPAÇÃO:")
    print(f"{'Código':<20} {'Densidade':<12} {'Área Op.':<12} {'Área Máx/Bico':<15} {'RTI (min)':<10}")
    print("-" * 80)
    for chave, c in CLASSES_RISCO_OCUPACAO.items():
        print(
            f"{chave:<20} "
            f"{formatar_fracao_decimal(Fraction(c['densidade_minima_mm_min'])) + ' mm/min':<12} "
            f"{str(c['area_operacao_minima_m2']) + ' m²':<12} "
            f"{formatar_fracao_decimal(Fraction(c['area_maxima_bico_m2'])) + ' m²':<15} "
            f"{str(c['tempo_minimo_rti_min']) + ' min':<10}"
        )

    print("\n2. FATORES K DE CHUVEIROS AUTOMÁTICOS:")
    print(f"{'Modelo':<10} {'Fator K':<10} {'Rosca':<15} {'Orifício (mm)':<15} {'Aplicação'}")
    print("-" * 80)
    for chave, k in FATORES_K_SPRINKLERS.items():
        print(
            f"{chave:<10} "
            f"{str(k['fator_k']):<10} "
            f"{str(k['rosca_nominal_pol']):<15} "
            f"{formatar_fracao_decimal(Fraction(k['orificio_nominal_mm'])) + ' mm':<15} "
            f"{str(k['aplicacao'])}"
        )

    print("\n3. TUBOS DE AÇO CARBONO NBR 5580:")
    print(f"{'Identificador':<15} {'DN (pol)':<12} {'DN (mm)':<10} {'Diâmetro Int. (mm)':<20} {'C Hazen-Williams'}")
    print("-" * 80)
    for chave, t in TUBOS_ACO_SPRINKLERS.items():
        print(
            f"{chave:<15} "
            f"{str(t['dn_pol']):<12} "
            f"{str(t['dn_mm']):<10} "
            f"{formatar_fracao_decimal(Fraction(t['diametro_interno_mm'])) + ' mm':<20} "
            f"{str(t['rugosidade_c'])}"
        )
    print("=" * 80)
    return 0


def comando_gerar_exemplo(args: argparse.Namespace) -> int:
    """Gera arquivo JSON com exemplo pronto para dimensionamento."""
    tipo = getattr(args, "tipo", "risco_leve")
    if tipo not in CLASSES_RISCO_OCUPACAO:
        tipo = "risco_leve"

    if tipo == "risco_ordinario_1":
        inst = InstalacaoSprinklers(
            projeto="Centro Comercial Paulista - Bloco Lojas",
            classe_risco="risco_ordinario_1",
            area_compartimento_m2=Fraction(500, 1),
            bico=BicoSprinkler(
                modelo_fator_k="K80",
                espacamento_s_m=Fraction(3, 1),
                espacamento_l_m=Fraction(35, 10),
            ),
            trechos=(
                TrechoRede(
                    identificador="SUCCAO_BOMBA",
                    tubo_id="4_pol",
                    comprimento_real_m=Fraction(8, 1),
                    desnivel_geometrico_m=Fraction(0, 1),
                    conexoes=ConexoesTrecho(joelho_90=2, valvula_gaveta=1),
                ),
                TrechoRede(
                    identificador="RECALQUE_VGA",
                    tubo_id="3_pol",
                    comprimento_real_m=Fraction(15, 1),
                    desnivel_geometrico_m=Fraction(4, 1),
                    conexoes=ConexoesTrecho(joelho_90=3, valvula_gaveta=1, valvula_retencao=1),
                    tem_vga=True,
                ),
                TrechoRede(
                    identificador="COLUNA_RISER",
                    tubo_id="3_pol",
                    comprimento_real_m=Fraction(25, 1),
                    desnivel_geometrico_m=Fraction(20, 1),
                    conexoes=ConexoesTrecho(te_passagem_direta=4),
                ),
                TrechoRede(
                    identificador="RAMAL_CRITICO",
                    tubo_id="2_pol",
                    comprimento_real_m=Fraction(18, 1),
                    desnivel_geometrico_m=Fraction(0, 1),
                    conexoes=ConexoesTrecho(joelho_90=2, te_saida_lateral=3),
                ),
            ),
            margem_desbalanceamento_pct=Fraction(15, 1),
            rendimento_bomba=Fraction(65, 100),
        )
    elif tipo == "risco_extra_1":
        inst = InstalacaoSprinklers(
            projeto="Centro Logístico Sul - Depósito Químico",
            classe_risco="risco_extra_1",
            area_compartimento_m2=Fraction(1200, 1),
            bico=BicoSprinkler(
                modelo_fator_k="K160",
                espacamento_s_m=Fraction(28, 10),
                espacamento_l_m=Fraction(3, 1),
            ),
            trechos=(
                TrechoRede(
                    identificador="SUCCAO_BOMBA",
                    tubo_id="6_pol",
                    comprimento_real_m=Fraction(12, 1),
                    desnivel_geometrico_m=Fraction(0, 1),
                    conexoes=ConexoesTrecho(joelho_90=2, valvula_gaveta=1),
                ),
                TrechoRede(
                    identificador="RECALQUE_VGA",
                    tubo_id="4_pol",
                    comprimento_real_m=Fraction(20, 1),
                    desnivel_geometrico_m=Fraction(5, 1),
                    conexoes=ConexoesTrecho(joelho_90=2, valvula_retencao=1, valvula_gaveta=1),
                    tem_vga=True,
                ),
                TrechoRede(
                    identificador="COLUNA_PRINCIPAL",
                    tubo_id="4_pol",
                    comprimento_real_m=Fraction(30, 1),
                    desnivel_geometrico_m=Fraction(12, 1),
                    conexoes=ConexoesTrecho(te_passagem_direta=5),
                ),
                TrechoRede(
                    identificador="SUBRAMAL_DISTRIBUICAO",
                    tubo_id="2_1_2_pol",
                    comprimento_real_m=Fraction(22, 1),
                    desnivel_geometrico_m=Fraction(0, 1),
                    conexoes=ConexoesTrecho(joelho_90=3, te_saida_lateral=4),
                ),
            ),
            margem_desbalanceamento_pct=Fraction(15, 1),
            rendimento_bomba=Fraction(65, 100),
        )
    else:
        inst = InstalacaoSprinklers(
            projeto="Edifício Escritórios Corporativos Faria Lima",
            classe_risco="risco_leve",
            area_compartimento_m2=Fraction(800, 1),
            bico=BicoSprinkler(
                modelo_fator_k="K80",
                espacamento_s_m=Fraction(35, 10),
                espacamento_l_m=Fraction(35, 10),
            ),
            trechos=(
                TrechoRede(
                    identificador="SUCCAO_BOMBA",
                    tubo_id="3_pol",
                    comprimento_real_m=Fraction(6, 1),
                    desnivel_geometrico_m=Fraction(0, 1),
                    conexoes=ConexoesTrecho(joelho_90=1, valvula_gaveta=1),
                ),
                TrechoRede(
                    identificador="BARRILETE_VGA",
                    tubo_id="2_1_2_pol",
                    comprimento_real_m=Fraction(12, 1),
                    desnivel_geometrico_m=Fraction(3, 1),
                    conexoes=ConexoesTrecho(joelho_90=2, valvula_retencao=1, valvula_gaveta=1),
                    tem_vga=True,
                ),
                TrechoRede(
                    identificador="COLUNA_PRUMADA",
                    tubo_id="2_1_2_pol",
                    comprimento_real_m=Fraction(24, 1),
                    desnivel_geometrico_m=Fraction(18, 1),
                    conexoes=ConexoesTrecho(te_passagem_direta=4),
                ),
                TrechoRede(
                    identificador="RAMAL_PAVIMENTO_TIPO",
                    tubo_id="1_1_2_pol",
                    comprimento_real_m=Fraction(15, 1),
                    desnivel_geometrico_m=Fraction(0, 1),
                    conexoes=ConexoesTrecho(joelho_90=2, te_saida_lateral=3),
                ),
            ),
            margem_desbalanceamento_pct=Fraction(15, 1),
            rendimento_bomba=Fraction(65, 100),
        )

    import json
    saida = json.dumps(instalacao_para_dict(inst), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    caminho_saida = getattr(args, "saida", None)
    if caminho_saida:
        p = Path(caminho_saida).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(saida, encoding="utf-8")
        print(f"Exemplo gravado com sucesso em '{p}'.")
    else:
        sys.stdout.write(saida)
    return 0


def comando_calcular(args: argparse.Namespace) -> int:
    """Executa o cálculo e dimensionamento da instalação."""
    caminho_entrada = Path(args.arquivo).resolve()
    if not caminho_entrada.exists():
        sys.stderr.write(f"Erro: arquivo de entrada '{caminho_entrada}' não encontrado.\n")
        return 1

    try:
        conteudo = caminho_entrada.read_text(encoding="utf-8")
        instalacao = decodificar_instalacao_json(conteudo)
        resultado = calcular_sprinklers_nbr10897(instalacao)
    except Exception as exc:
        sys.stderr.write(f"Erro no processamento hidráulico: {exc}\n")
        return 2

    # Saídas solicitadas
    relatorio_txt = gerar_relatorio_texto(resultado)

    if args.saida_txt:
        p_txt = Path(args.saida_txt).resolve()
        p_txt.parent.mkdir(parents=True, exist_ok=True)
        p_txt.write_text(relatorio_txt, encoding="utf-8")
        print(f"[TXT] Relatório gravado em '{p_txt}'")

    if args.saida_json:
        p_json = Path(args.saida_json).resolve()
        p_json.parent.mkdir(parents=True, exist_ok=True)
        p_json.write_text(codificar_resultado_json(resultado), encoding="utf-8")
        print(f"[JSON] Resultado gravado em '{p_json}'")

    if args.saida_csv:
        p_csv = Path(args.saida_csv).resolve()
        p_csv.parent.mkdir(parents=True, exist_ok=True)
        p_csv.write_text(gerar_csv_trechos(resultado), encoding="utf-8")
        print(f"[CSV] Planilha de trechos gravada em '{p_csv}'")

    svg_conteudo: str | None = None
    if args.saida_svg or args.pacote_zip:
        svg_conteudo = gerar_painel_svg(resultado)

    if args.saida_svg and svg_conteudo:
        p_svg = Path(args.saida_svg).resolve()
        p_svg.parent.mkdir(parents=True, exist_ok=True)
        p_svg.write_text(svg_conteudo, encoding="utf-8")
        print(f"[SVG] Painel executivo gravado em '{p_svg}'")

    if args.pacote_zip:
        p_zip = Path(args.pacote_zip).resolve()
        criar_pacote_zip_deterministico(
            p_zip,
            resultado,
            conteudo_svg=svg_conteudo,
            sobrescrever=True,
        )
        print(f"[ZIP] Pacote determinístico gerado em '{p_zip}'")

    # Exibe relatório no console
    print(relatorio_txt)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = argparse.ArgumentParser(
        prog="sprinklers-nbr10897",
        description="Dimensionamento de Chuveiros Automáticos (Sprinklers) - ABNT NBR 10897:2020",
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    # Subcomando 'calcular'
    parser_calc = subparsers.add_parser("calcular", help="Calcula instalação de sprinklers a partir de arquivo JSON")
    parser_calc.add_argument("arquivo", help="Caminho do arquivo JSON de instalação")
    parser_calc.add_argument("--saida-json", help="Exporta resultado em formato JSON RFC 8259")
    parser_calc.add_argument("--saida-txt", help="Exporta relatório técnico executivo em texto puro")
    parser_calc.add_argument("--saida-csv", help="Exporta tabela de trechos hidráulicos em CSV")
    parser_calc.add_argument("--saida-svg", help="Exporta painel vetorial executivo 1440x900 em SVG")
    parser_calc.add_argument("--pacote-zip", help="Gera pacote determinístico completo em arquivo ZIP")
    parser_calc.set_defaults(funcao=comando_calcular)

    # Subcomando 'catalogo'
    parser_cat = subparsers.add_parser("catalogo", help="Exibe parâmetros normativos da NBR 10897")
    parser_cat.set_defaults(funcao=comando_catalogo)

    # Subcomando 'gerar-exemplo'
    parser_ex = subparsers.add_parser("gerar-exemplo", help="Gera arquivo de entrada JSON de exemplo")
    parser_ex.add_argument(
        "--tipo",
        choices=["risco_leve", "risco_ordinario_1", "risco_extra_1"],
        default="risco_leve",
        help="Tipo de ocupação de exemplo",
    )
    parser_ex.add_argument("--saida", help="Caminho de saída para o arquivo JSON gerado")
    parser_ex.set_defaults(funcao=comando_gerar_exemplo)

    args = parser.parse_args(argv)
    return int(args.funcao(args))


if __name__ == "__main__":
    sys.exit(main())
