"""Módulo de exportação de relatórios, planilhas CSV e pacotes ZIP determinísticos.

Implementa:
- Relatório técnico em texto plano (pt-BR);
- Planilha CSV sanitizada contra injeção de fórmulas (=, +, -, @, \\t, \\r);
- Pacote ZIP determinístico com carimbo temporal fixo (2026-01-01 00:00:00) e O_EXCL.
"""

from __future__ import annotations

import csv
from datetime import datetime
from fractions import Fraction
import io
import os
from pathlib import Path
import zipfile

from sprinklers_nbr10897.codecs import codificar_resultado_json
from sprinklers_nbr10897.models import ResultadoDimensionamentoSprinklers

DATA_FIXA_ZIP = (2026, 1, 1, 0, 0, 0)


def formatar_fracao_decimal(f: Fraction, casas: int = 2) -> str:
    """Converte fração para string decimal pt-BR com vírgula sem usar float."""
    if f < 0:
        sinal = "-"
        f_pos = -f
    else:
        sinal = ""
        f_pos = f

    fator = 10**casas
    # Arredondamento da metade para cima via inteiros
    num_arredondado = (f_pos.numerator * fator * 2 + f_pos.denominator) // (f_pos.denominator * 2)
    parte_inteira = num_arredondado // fator
    resto = num_arredondado % fator
    resto_str = str(resto).zfill(casas)
    return f"{sinal}{parte_inteira},{resto_str}"


def sanitizar_campo_csv(val: str) -> str:
    """Sanitiza strings para CSV prevenindo ataques de CSV Formula Injection."""
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def gerar_relatorio_texto(res: ResultadoDimensionamentoSprinklers) -> str:
    """Gera relatório técnico executivo em texto puro formatado (pt-BR)."""
    linhas: list[str] = [
        "=" * 80,
        "    LOFRANO TECNOLOGIA - ENGENHARIA DE PROTEÇÃO CONTRA INCÊNDIO",
        "    DIMENSIONAMENTO DE CHUVEIROS AUTOMÁTICOS (SPRINKLERS) - ABNT NBR 10897:2020",
        "=" * 80,
        f"Projeto: {res.projeto}",
        f"Classe de Risco: {res.nome_classe_risco} ({res.classe_risco})",
        f"Conformidade Normativa: {'CONFORME' if res.atende_norma else 'ATENÇÃO/NÃO CONFORME'}",
        "-" * 80,
        "1. PARÂMETROS BÁSICOS E HIDRÁULICA DO BICHO CRÍTICO",
        f"  - Densidade mínima requerida:       {formatar_fracao_decimal(res.densidade_adotada_mm_min)} mm/min (L/min/m²)",
        f"  - Área de operação adotada:         {formatar_fracao_decimal(res.area_operacao_adotada_m2)} m²",
        f"  - Área de cobertura por bico:       {formatar_fracao_decimal(res.area_por_bico_m2)} m²",
        f"  - Fator K do sprinkler:             K{res.fator_k}",
        f"  - Pressão residual no bico crítico: {formatar_fracao_decimal(res.pressao_minima_bico_mca)} mca",
        f"  - Vazão unitária do bico crítico:   {formatar_fracao_decimal(res.vazao_bico_critico_l_min)} L/min",
        "-" * 80,
        "2. DEMANDA DE VAZÃO E RESERVA TÉCNICA DE INCÊNDIO (RTI)",
        f"  - Bicos em operação simultânea:     {res.numero_bicos_operacao} bicos",
        f"  - Vazão dos bicos na área:          {formatar_fracao_decimal(res.vazao_bicos_l_min)} L/min",
        f"  - Vazão c/ desbalanceamento (+15%): {formatar_fracao_decimal(res.vazao_sprinklers_desbalanceada_l_min)} L/min",
        f"  - Vazão para hidrantes adicionais:  {formatar_fracao_decimal(res.vazao_hidrantes_adicionais_l_min)} L/min",
        f"  - Vazão TOTAL do sistema:           {formatar_fracao_decimal(res.vazao_total_sistema_l_min)} L/min",
        f"  - Tempo de autonomia da RTI:        {res.tempo_minimo_rti_min} minutos",
        f"  - Volume mínimo de RTI necessário:  {formatar_fracao_decimal(res.volume_rti_m3)} m³ ({formatar_fracao_decimal(res.volume_rti_m3 * 1000, 0)} Litros)",
        "-" * 80,
        "3. TRECHOS DE TUBULAÇÃO E PERDAS DE CARGA (NBR 5580 / HAZEN-WILLIAMS)",
        f"{'Trecho':<20} {'DN':<8} {'L.Real(m)':<10} {'L.Eq(m)':<10} {'L.Tot(m)':<10} {'J(mca/m)':<10} {'ΔH(mca)':<10} {'v(m/s)':<8}",
        "-" * 80,
    ]

    for t in res.trechos:
        linhas.append(
            f"{t.identificador:<20} {t.dn_pol:<8} "
            f"{formatar_fracao_decimal(t.comprimento_real_m):<10} "
            f"{formatar_fracao_decimal(t.comprimento_equivalente_m):<10} "
            f"{formatar_fracao_decimal(t.comprimento_total_m):<10} "
            f"{formatar_fracao_decimal(t.perda_unitaria_mca_m, 4):<10} "
            f"{formatar_fracao_decimal(t.perda_carga_mca):<10} "
            f"{formatar_fracao_decimal(t.velocidade_m_s):<8}"
        )

    linhas.extend([
        "-" * 80,
        "4. SISTEMA DE PRESSURIZAÇÃO (MOTO-BOMBA PRINCIPAL)",
        f"  - Perda de carga total em tubos:    {formatar_fracao_decimal(res.perda_carga_total_tubulacao_mca)} mca",
        f"  - Desnível geométrico total:        {formatar_fracao_decimal(res.desnivel_geometrico_total_m)} m",
        f"  - Pressão mínima bico crítico:      {formatar_fracao_decimal(res.pressao_minima_bico_mca)} mca",
        f"  - Altura Manométrica Total (Hman):  {formatar_fracao_decimal(res.altura_manometrica_total_mca)} mca",
        f"  - Potência calculada da bomba:      {formatar_fracao_decimal(res.potencia_bomba_cv)} cv",
        f"  - Motor comercial recomendado:      {res.potencia_comercial_bomba_cv} cv",
        "-" * 80,
        "5. OBSERVAÇÕES E PARECER TÉCNICO",
    ])
    for obs in res.observacoes:
        linhas.append(f"  * {obs}")
    linhas.extend([
        "=" * 80,
        "Emitido via Lofrano Tecnologia - Conforme ABNT NBR 10897:2020",
        "=" * 80,
        "",
    ])
    return "\n".join(linhas)


def gerar_csv_trechos(res: ResultadoDimensionamentoSprinklers) -> str:
    """Gera planilha CSV com os trechos hidráulicos e sanitização de fórmulas."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", lineterminator="\n")

    writer.writerow([
        sanitizar_campo_csv("identificador"),
        sanitizar_campo_csv("tubo_id"),
        sanitizar_campo_csv("dn_pol"),
        sanitizar_campo_csv("diametro_interno_mm"),
        sanitizar_campo_csv("vazao_l_min"),
        sanitizar_campo_csv("velocidade_m_s"),
        sanitizar_campo_csv("comprimento_real_m"),
        sanitizar_campo_csv("comprimento_equivalente_m"),
        sanitizar_campo_csv("comprimento_total_m"),
        sanitizar_campo_csv("perda_unitaria_mca_m"),
        sanitizar_campo_csv("perda_carga_mca"),
        sanitizar_campo_csv("desnivel_m"),
    ])

    for t in res.trechos:
        writer.writerow([
            sanitizar_campo_csv(t.identificador),
            sanitizar_campo_csv(t.tubo_id),
            sanitizar_campo_csv(t.dn_pol),
            sanitizar_campo_csv(formatar_fracao_decimal(t.diametro_interno_mm)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.vazao_l_min)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.velocidade_m_s)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.comprimento_real_m)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.comprimento_equivalente_m)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.comprimento_total_m)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.perda_unitaria_mca_m, 4)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.perda_carga_mca)),
            sanitizar_campo_csv(formatar_fracao_decimal(t.desnivel_m)),
        ])

    return buffer.getvalue()


def criar_pacote_zip_deterministico(
    caminho_saida: str | Path,
    res: ResultadoDimensionamentoSprinklers,
    conteudo_svg: str | None = None,
    sobrescrever: bool = True,
) -> Path:
    """Gera pacote ZIP com timestamp determinístico e modo seguro de criação."""
    caminho = Path(caminho_saida).resolve()
    caminho.parent.mkdir(parents=True, exist_ok=True)

    if caminho.exists():
        if sobrescrever:
            caminho.unlink()
        else:
            raise FileExistsError(f"Arquivo de destino '{caminho}' já existe.")

    # Cria arquivo via descritor de arquivo O_CREAT | O_EXCL
    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    fd = os.open(str(caminho), flags, 0o644)
    with os.fdopen(fd, "wb") as f_out:
        with zipfile.ZipFile(f_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # 1. Relatório técnico em texto
            relatorio_txt = gerar_relatorio_texto(res).encode("utf-8")
            zinfo_txt = zipfile.ZipInfo(filename="relatorio_tecnico.txt", date_time=DATA_FIXA_ZIP)
            zinfo_txt.external_attr = 0o644 << 16
            zf.writestr(zinfo_txt, relatorio_txt)

            # 2. Resultado JSON canônico
            resultado_json = codificar_resultado_json(res).encode("utf-8")
            zinfo_json = zipfile.ZipInfo(filename="resultado.json", date_time=DATA_FIXA_ZIP)
            zinfo_json.external_attr = 0o644 << 16
            zf.writestr(zinfo_json, resultado_json)

            # 3. CSV dos trechos
            csv_trechos = gerar_csv_trechos(res).encode("utf-8")
            zinfo_csv = zipfile.ZipInfo(filename="trechos.csv", date_time=DATA_FIXA_ZIP)
            zinfo_csv.external_attr = 0o644 << 16
            zf.writestr(zinfo_csv, csv_trechos)

            # 4. Painel vetorial SVG (opcional)
            if conteudo_svg:
                zinfo_svg = zipfile.ZipInfo(filename="painel_sistema.svg", date_time=DATA_FIXA_ZIP)
                zinfo_svg.external_attr = 0o644 << 16
                zf.writestr(zinfo_svg, conteudo_svg.encode("utf-8"))

    return caminho
