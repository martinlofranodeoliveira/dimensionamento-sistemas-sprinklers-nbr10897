"""Constantes e parâmetros normativos da ABNT NBR 10897:2020.

Define classes de risco de ocupação (Risco Leve, Ordinário 1 e 2, Extra 1 e 2),
fatores K de chuveiros automáticos (sprinklers), tubulações de aço NBR 5580,
conexoes equivalentes e perda em Válvulas de Governo e Alarme (VGA).
Aritmética estritamente racional exata (Fraction).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Final

# Densidade da água e rendimento nominal da moto-bomba de sprinklers
DENSIDADE_AGUA_KGF_M3: Final[int] = 1000
RENDIMENTO_PADRAO_BOMBA: Final[Fraction] = Fraction(65, 100)  # 65%

# Tabela 1 e Tabela 4 da ABNT NBR 10897:2020 - Classes de Risco de Ocupação
CLASSES_RISCO_OCUPACAO: Final[dict[str, dict[str, Fraction | int | str]]] = {
    "risco_leve": {
        "codigo": "risco_leve",
        "nome": "Risco Leve (RL) - Habitações, Hotéis, Escritórios, Escolas",
        "densidade_minima_mm_min": Fraction(41, 10),      # 4,1 mm/min (L/min/m²)
        "area_operacao_minima_m2": 139,                   # 139 m²
        "area_maxima_bico_m2": Fraction(186, 10),         # 18,6 m²
        "tempo_minimo_rti_min": 30,                       # 30 minutos
        "vazao_hidrantes_adicionais_l_min": Fraction(380, 1), # 380 L/min
        "pressao_minima_bico_mca": Fraction(5, 1),        # 0,5 bar = 5 mca
    },
    "risco_ordinario_1": {
        "codigo": "risco_ordinario_1",
        "nome": "Risco Ordinário Grupo 1 (RO1) - Comércios, Restaurantes, Garagens",
        "densidade_minima_mm_min": Fraction(61, 10),      # 6,1 mm/min
        "area_operacao_minima_m2": 139,
        "area_maxima_bico_m2": Fraction(12, 1),           # 12,0 m²
        "tempo_minimo_rti_min": 60,                       # 60 minutos
        "vazao_hidrantes_adicionais_l_min": Fraction(950, 1), # 950 L/min
        "pressao_minima_bico_mca": Fraction(5, 1),
    },
    "risco_ordinario_2": {
        "codigo": "risco_ordinario_2",
        "nome": "Risco Ordinário Grupo 2 (RO2) - Lojas de Departamentos, Depósitos Leves",
        "densidade_minima_mm_min": Fraction(81, 10),      # 8,1 mm/min
        "area_operacao_minima_m2": 139,
        "area_maxima_bico_m2": Fraction(12, 1),
        "tempo_minimo_rti_min": 60,
        "vazao_hidrantes_adicionais_l_min": Fraction(950, 1),
        "pressao_minima_bico_mca": Fraction(5, 1),
    },
    "risco_extra_1": {
        "codigo": "risco_extra_1",
        "nome": "Risco Extra Grupo 1 (RE1) - Indústrias Químicas, Hangares",
        "densidade_minima_mm_min": Fraction(122, 10),     # 12,2 mm/min
        "area_operacao_minima_m2": 232,                   # 232 m²
        "area_maxima_bico_m2": Fraction(9, 1),            # 9,0 m²
        "tempo_minimo_rti_min": 90,                       # 90 minutos
        "vazao_hidrantes_adicionais_l_min": Fraction(1900, 1), # 1900 L/min
        "pressao_minima_bico_mca": Fraction(7, 1),        # 0,7 bar = 7 mca
    },
    "risco_extra_2": {
        "codigo": "risco_extra_2",
        "nome": "Risco Extra Grupo 2 (RE2) - Armazéns com Plásticos, Líquidos Inflamáveis",
        "densidade_minima_mm_min": Fraction(163, 10),     # 16,3 mm/min
        "area_operacao_minima_m2": 232,
        "area_maxima_bico_m2": Fraction(9, 1),
        "tempo_minimo_rti_min": 120,                      # 120 minutos
        "vazao_hidrantes_adicionais_l_min": Fraction(1900, 1),
        "pressao_minima_bico_mca": Fraction(7, 1),
    },
}

# Coeficientes de Descarga Fator K de Chuveiros Automáticos (NBR 10897)
# Q = K * sqrt(P) [L/min, bar] => P_mca = 10 * (Q / K)^2
FATORES_K_SPRINKLERS: Final[dict[str, dict[str, int | str | Fraction]]] = {
    "K80": {
        "fator_k": 80,
        "rosca_nominal_pol": "1/2 pol",
        "orificio_nominal_mm": Fraction(127, 10),   # 12,7 mm
        "aplicacao": "Padrão para Risco Leve e Ordinário",
    },
    "K115": {
        "fator_k": 115,
        "rosca_nominal_pol": "17/32 pol",
        "orificio_nominal_mm": Fraction(135, 10),   # 13,5 mm
        "aplicacao": "Risco Ordinário e Extra",
    },
    "K160": {
        "fator_k": 160,
        "rosca_nominal_pol": "3/4 pol",
        "orificio_nominal_mm": Fraction(159, 10),   # 15,9 mm
        "aplicacao": "Risco Extra e Galpões Industriais",
    },
    "K200": {
        "fator_k": 200,
        "rosca_nominal_pol": "3/4 pol",
        "orificio_nominal_mm": Fraction(190, 10),   # 19,0 mm
        "aplicacao": "Galpões e Áreas de Armazenamento",
    },
}

# Tubos de Aço Carbono NBR 5580 para Redes de Sprinklers
TUBOS_ACO_SPRINKLERS: Final[dict[str, dict[str, str | int | Fraction]]] = {
    "1_pol": {
        "dn_pol": "1 pol",
        "dn_mm": 25,
        "diametro_interno_mm": Fraction(273, 10),
        "rugosidade_c": 120,
    },
    "1_1_4_pol": {
        "dn_pol": "1 1/4 pol",
        "dn_mm": 32,
        "diametro_interno_mm": Fraction(360, 10),
        "rugosidade_c": 120,
    },
    "1_1_2_pol": {
        "dn_pol": "1 1/2 pol",
        "dn_mm": 40,
        "diametro_interno_mm": Fraction(419, 10),
        "rugosidade_c": 120,
    },
    "2_pol": {
        "dn_pol": "2 pol",
        "dn_mm": 50,
        "diametro_interno_mm": Fraction(530, 10),
        "rugosidade_c": 120,
    },
    "2_1_2_pol": {
        "dn_pol": "2 1/2 pol",
        "dn_mm": 65,
        "diametro_interno_mm": Fraction(687, 10),
        "rugosidade_c": 120,
    },
    "3_pol": {
        "dn_pol": "3 pol",
        "dn_mm": 80,
        "diametro_interno_mm": Fraction(809, 10),
        "rugosidade_c": 120,
    },
    "4_pol": {
        "dn_pol": "4 pol",
        "dn_mm": 100,
        "diametro_interno_mm": Fraction(1053, 10),
        "rugosidade_c": 120,
    },
    "6_pol": {
        "dn_pol": "6 pol",
        "dn_mm": 150,
        "diametro_interno_mm": Fraction(1554, 10),
        "rugosidade_c": 120,
    },
}

# Comprimentos equivalentes em metros para conexões de aço (Tabela B.1)
CONEXOES_EQUIVALENTES_SPRINKLERS_M: Final[dict[str, dict[str, Fraction]]] = {
    "1_pol": {
        "joelho_90": Fraction(8, 10),
        "te_passagem_direta": Fraction(5, 10),
        "te_saida_lateral": Fraction(15, 10),
        "valvula_gaveta": Fraction(2, 10),
        "valvula_retencao": Fraction(25, 10),
    },
    "1_1_4_pol": {
        "joelho_90": Fraction(11, 10),
        "te_passagem_direta": Fraction(6, 10),
        "te_saida_lateral": Fraction(20, 10),
        "valvula_gaveta": Fraction(2, 10),
        "valvula_retencao": Fraction(32, 10),
    },
    "1_1_2_pol": {
        "joelho_90": Fraction(15, 10),
        "te_passagem_direta": Fraction(8, 10),
        "te_saida_lateral": Fraction(32, 10),
        "valvula_gaveta": Fraction(3, 10),
        "valvula_retencao": Fraction(40, 10),
    },
    "2_pol": {
        "joelho_90": Fraction(20, 10),
        "te_passagem_direta": Fraction(10, 10),
        "te_saida_lateral": Fraction(41, 10),
        "valvula_gaveta": Fraction(4, 10),
        "valvula_retencao": Fraction(52, 10),
    },
    "2_1_2_pol": {
        "joelho_90": Fraction(25, 10),
        "te_passagem_direta": Fraction(14, 10),
        "te_saida_lateral": Fraction(52, 10),
        "valvula_gaveta": Fraction(5, 10),
        "valvula_retencao": Fraction(65, 10),
    },
    "3_pol": {
        "joelho_90": Fraction(31, 10),
        "te_passagem_direta": Fraction(17, 10),
        "te_saida_lateral": Fraction(66, 10),
        "valvula_gaveta": Fraction(7, 10),
        "valvula_retencao": Fraction(79, 10),
    },
    "4_pol": {
        "joelho_90": Fraction(40, 10),
        "te_passagem_direta": Fraction(23, 10),
        "te_saida_lateral": Fraction(87, 10),
        "valvula_gaveta": Fraction(9, 10),
        "valvula_retencao": Fraction(104, 10),
    },
    "6_pol": {
        "joelho_90": Fraction(55, 10),
        "te_passagem_direta": Fraction(32, 10),
        "te_saida_lateral": Fraction(125, 10),
        "valvula_gaveta": Fraction(12, 10),
        "valvula_retencao": Fraction(150, 10),
    },
}

# Perda equivalente em metros de tubo da Válvula de Governo e Alarme (VGA)
PERDA_VGA_METROS_EQUIVALENTES: Final[dict[str, Fraction]] = {
    "2_1_2_pol": Fraction(8, 1),
    "3_pol": Fraction(10, 1),
    "4_pol": Fraction(12, 1),
    "6_pol": Fraction(16, 1),
}
