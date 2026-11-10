"""Pacote sprinklers_nbr10897 - Dimensionamento de Chuveiros Automáticos (ABNT NBR 10897:2020).

Aritmética estritamente racional exata (Fraction e inteiros). Zero float.
Lofrano Tecnologia 2026.
"""

from __future__ import annotations

from sprinklers_nbr10897.calculator import (
    calcular_sprinklers_nbr10897,
    raiz_quadrada_frac,
    teto_divisao_frac,
)
from sprinklers_nbr10897.codecs import (
    codificar_resultado_json,
    decodificar_instalacao_json,
    instalacao_para_dict,
    resultado_para_dict,
)
from sprinklers_nbr10897.constants import (
    CLASSES_RISCO_OCUPACAO,
    CONEXOES_EQUIVALENTES_SPRINKLERS_M,
    DENSIDADE_AGUA_KGF_M3,
    FATORES_K_SPRINKLERS,
    PERDA_VGA_METROS_EQUIVALENTES,
    RENDIMENTO_PADRAO_BOMBA,
    TUBOS_ACO_SPRINKLERS,
)
from sprinklers_nbr10897.exporters import (
    criar_pacote_zip_deterministico,
    formatar_fracao_decimal,
    gerar_csv_trechos,
    gerar_relatorio_texto,
    sanitizar_campo_csv,
)
from sprinklers_nbr10897.models import (
    BicoSprinkler,
    ConexoesTrecho,
    InstalacaoSprinklers,
    ResultadoDimensionamentoSprinklers,
    ResultadoTrecho,
    TrechoRede,
)
from sprinklers_nbr10897.svg_generator import gerar_painel_svg

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "BicoSprinkler",
    "ConexoesTrecho",
    "TrechoRede",
    "InstalacaoSprinklers",
    "ResultadoTrecho",
    "ResultadoDimensionamentoSprinklers",
    "calcular_sprinklers_nbr10897",
    "raiz_quadrada_frac",
    "teto_divisao_frac",
    "decodificar_instalacao_json",
    "codificar_resultado_json",
    "instalacao_para_dict",
    "resultado_para_dict",
    "gerar_relatorio_texto",
    "gerar_csv_trechos",
    "criar_pacote_zip_deterministico",
    "formatar_fracao_decimal",
    "sanitizar_campo_csv",
    "gerar_painel_svg",
    "CLASSES_RISCO_OCUPACAO",
    "FATORES_K_SPRINKLERS",
    "TUBOS_ACO_SPRINKLERS",
    "CONEXOES_EQUIVALENTES_SPRINKLERS_M",
    "PERDA_VGA_METROS_EQUIVALENTES",
    "DENSIDADE_AGUA_KGF_M3",
    "RENDIMENTO_PADRAO_BOMBA",
]
