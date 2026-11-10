"""Mecanismo de cálculo hidráulico da ABNT NBR 10897:2020.

Implementa dimensionamento hidráulico de chuveiros automáticos (sprinklers),
cálculo de vazão por bico crítico, pressão de acionamento, número de bicos em operação,
vazão total com sobrepressão de desbalanceamento, reserva técnica de incêndio (RTI),
perdas de carga contínuas e localizadas em tubos de aço NBR 5580, altura manométrica total
e dimensionamento da moto-bomba com rendimento.
Aritmética estritamente exata (Fraction e inteiros). Zero float.
"""

from __future__ import annotations

from fractions import Fraction
import math

from sprinklers_nbr10897.constants import (
    CLASSES_RISCO_OCUPACAO,
    CONEXOES_EQUIVALENTES_SPRINKLERS_M,
    FATORES_K_SPRINKLERS,
    PERDA_VGA_METROS_EQUIVALENTES,
    RENDIMENTO_PADRAO_BOMBA,
    TUBOS_ACO_SPRINKLERS,
)
from sprinklers_nbr10897.models import (
    InstalacaoSprinklers,
    ResultadoDimensionamentoSprinklers,
    ResultadoTrecho,
)

# Aproximação racional de pi: 355 / 113 (precisão de 7 dígitos)
PI_RACIONAL = Fraction(355, 113)

# Potências comerciais padronizadas para moto-bombas (em cv inteiros ou fracionários)
POTENCIAS_COMERCIAIS_CV: tuple[int, ...] = (
    1, 2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 200, 250
)


def raiz_quadrada_frac(val: Fraction, escala: int = 1_000_000) -> Fraction:
    """Calcula a raiz quadrada de uma fração com precisão racional exata.

    Se for quadrado perfeito, retorna a raiz exata.
    Caso contrário, calcula aproximação racional com escala inteira (isqrt) sem conversão para float
    e sem risco de explosão de dígitos.
    """
    if val < 0:
        raise ValueError("Não é possível calcular raiz quadrada de fração negativa.")
    if val == 0:
        return Fraction(0, 1)

    # Verifica se os termos são quadrados perfeitos exatos
    sq_num = math.isqrt(val.numerator)
    sq_den = math.isqrt(val.denominator)
    if sq_num * sq_num == val.numerator and sq_den * sq_den == val.denominator:
        return Fraction(sq_num, sq_den)

    # Para irracionais, aproximação racional direta com escala inteira
    s2 = escala * escala
    raiz_escalada = math.isqrt(val.numerator * val.denominator * s2)
    return Fraction(raiz_escalada, val.denominator * escala)


def teto_divisao_frac(num: Fraction, den: Fraction) -> int:
    """Retorna o menor inteiro maior ou igual a num / den."""
    if den == 0:
        raise ZeroDivisionError("Divisão por zero em fração.")
    f = num / den
    # Parte inteira com correção para frações positivas
    div_int = f.numerator // f.denominator
    if f.numerator % f.denominator != 0 and f > 0:
        div_int += 1
    return div_int


def calcular_sprinklers_nbr10897(
    instalacao: InstalacaoSprinklers,
) -> ResultadoDimensionamentoSprinklers:
    """Executa o dimensionamento hidráulico normativo de sprinklers NBR 10897:2020.

    Retorna relatório e métricas completas com aritmética 100% racional.
    """
    # 1. Validação da classe de risco
    if instalacao.classe_risco not in CLASSES_RISCO_OCUPACAO:
        classes_validas = ", ".join(CLASSES_RISCO_OCUPACAO.keys())
        raise ValueError(
            f"Classe de risco '{instalacao.classe_risco}' inválida. Opções: {classes_validas}."
        )

    info_risco = CLASSES_RISCO_OCUPACAO[instalacao.classe_risco]
    nome_risco = str(info_risco["nome"])
    densidade_min_mm_min = Fraction(info_risco["densidade_minima_mm_min"])
    area_operacao_min_m2 = Fraction(int(info_risco["area_operacao_minima_m2"]), 1)
    area_max_bico_m2 = Fraction(info_risco["area_maxima_bico_m2"])
    tempo_rti_min = int(info_risco["tempo_minimo_rti_min"])
    vazao_hidrantes_l_min = Fraction(info_risco["vazao_hidrantes_adicionais_l_min"])
    pressao_min_norma_mca = Fraction(info_risco["pressao_minima_bico_mca"])

    # 2. Validação do bico adotado
    if instalacao.bico.modelo_fator_k not in FATORES_K_SPRINKLERS:
        bicos_validos = ", ".join(FATORES_K_SPRINKLERS.keys())
        raise ValueError(
            f"Bico '{instalacao.bico.modelo_fator_k}' inválido. Opções: {bicos_validos}."
        )

    info_bico = FATORES_K_SPRINKLERS[instalacao.bico.modelo_fator_k]
    fator_k = int(info_bico["fator_k"])

    observacoes: list[str] = []
    atende_norma = True

    # 3. Verificação da área máxima de cobertura por bico
    area_bico_m2 = instalacao.bico.area_cobertura_m2
    if area_bico_m2 > area_max_bico_m2:
        observacoes.append(
            f"ALERTA: Área de cobertura por bico ({area_bico_m2} m²) supera o limite normativo "
            f"de {area_max_bico_m2} m² para a classe {nome_risco}."
        )
        atende_norma = False

    # 4. Área de cálculo (operação)
    area_operacao_adotada = min(instalacao.area_compartimento_m2, area_operacao_min_m2)
    if instalacao.area_compartimento_m2 < area_operacao_min_m2:
        observacoes.append(
            f"Compartimento com área ({instalacao.area_compartimento_m2} m²) menor que a área "
            f"de operação normativa ({area_operacao_min_m2} m²). Dimensionado pela área total do compartimento."
        )

    # 5. Vazão mínima do bico crítico pela densidade normativa
    # q = densidade [mm/min = L/min/m²] * area_bico [m²]
    vazao_densidade_l_min = densidade_min_mm_min * area_bico_m2

    # Pressão necessária para gerar vazão de densidade com Fator K:
    # q = K * sqrt(P_bar) => P_bar = (q / K)^2 => P_mca = 10 * (q / K)^2
    pressao_requerida_densidade_mca = Fraction(10, 1) * (vazao_densidade_l_min**2) / Fraction(fator_k**2, 1)

    if pressao_requerida_densidade_mca < pressao_min_norma_mca:
        # A pressão residual mínima normativa governa o bico crítico
        pressao_adotada_bico_mca = pressao_min_norma_mca
        # Recalcula a vazão crítica a partir da pressão mínima normativa
        # q = K * sqrt(P_mca / 10)
        p_bar = pressao_min_norma_mca / Fraction(10, 1)
        sqrt_p = raiz_quadrada_frac(p_bar)
        vazao_bico_critico_l_min = Fraction(fator_k, 1) * sqrt_p
        observacoes.append(
            f"Pressão governada pelo mínimo normativo de {pressao_min_norma_mca} mca "
            f"(vazão aumentada de {vazao_densidade_l_min} L/min para {vazao_bico_critico_l_min} L/min)."
        )
    else:
        pressao_adotada_bico_mca = pressao_requerida_densidade_mca
        vazao_bico_critico_l_min = vazao_densidade_l_min

    # 6. Quantidade de bicos na área de cálculo
    numero_bicos_operacao = max(1, teto_divisao_frac(area_operacao_adotada, area_bico_m2))

    # 7. Vazão do conjunto de bicos e aplicação de desbalanceamento (+15% padrão)
    vazao_bicos_l_min = Fraction(numero_bicos_operacao, 1) * vazao_bico_critico_l_min
    fator_desbalanceamento = Fraction(1, 1) + (instalacao.margem_desbalanceamento_pct / Fraction(100, 1))
    vazao_sprinklers_desbalanceada_l_min = vazao_bicos_l_min * fator_desbalanceamento

    # 8. Vazão total do sistema (sprinklers + hidrantes adicionais)
    vazao_total_sistema_l_min = vazao_sprinklers_desbalanceada_l_min + vazao_hidrantes_l_min

    # 9. Volume de Reserva Técnica de Incêndio (RTI) em m³
    # Volume = (Q_total [L/min] * tempo [min]) / 1000 [L/m³]
    volume_rti_m3 = (vazao_total_sistema_l_min * Fraction(tempo_rti_min, 1)) / Fraction(1000, 1)

    # 10. Perda de carga por trecho de tubulação
    resultados_trechos: list[ResultadoTrecho] = []
    perda_carga_total_tubos = Fraction(0, 1)
    desnivel_total = Fraction(0, 1)

    for trecho in instalacao.trechos:
        if trecho.tubo_id not in TUBOS_ACO_SPRINKLERS:
            tubos_validos = ", ".join(TUBOS_ACO_SPRINKLERS.keys())
            raise ValueError(
                f"Tubo '{trecho.tubo_id}' no trecho '{trecho.identificador}' inválido. "
                f"Opções: {tubos_validos}."
            )

        info_tubo = TUBOS_ACO_SPRINKLERS[trecho.tubo_id]
        dn_pol = str(info_tubo["dn_pol"])
        diametro_int_mm = Fraction(info_tubo["diametro_interno_mm"])
        diametro_int_m = diametro_int_mm / Fraction(1000, 1)

        # Comprimento equivalente de conexões
        comp_eq_conexoes = Fraction(0, 1)
        if trecho.tubo_id in CONEXOES_EQUIVALENTES_SPRINKLERS_M:
            eq_map = CONEXOES_EQUIVALENTES_SPRINKLERS_M[trecho.tubo_id]
            comp_eq_conexoes += Fraction(trecho.conexoes.joelho_90, 1) * eq_map["joelho_90"]
            comp_eq_conexoes += Fraction(trecho.conexoes.te_passagem_direta, 1) * eq_map["te_passagem_direta"]
            comp_eq_conexoes += Fraction(trecho.conexoes.te_saida_lateral, 1) * eq_map["te_saida_lateral"]
            comp_eq_conexoes += Fraction(trecho.conexoes.valvula_gaveta, 1) * eq_map["valvula_gaveta"]
            comp_eq_conexoes += Fraction(trecho.conexoes.valvula_retencao, 1) * eq_map["valvula_retencao"]

        # Adiciona perda de VGA se aplicável
        if trecho.tem_vga:
            perda_vga_m = PERDA_VGA_METROS_EQUIVALENTES.get(trecho.tubo_id, Fraction(10, 1))
            comp_eq_conexoes += perda_vga_m

        comp_total_m = trecho.comprimento_real_m + comp_eq_conexoes

        # Velocidade de escoamento v = Q / A [m/s]
        # Q em m³/s = vazao_sprinklers_desbalanceada / 60.000
        q_m3_s = vazao_sprinklers_desbalanceada_l_min / Fraction(60000, 1)
        area_secao_m2 = (PI_RACIONAL * (diametro_int_m**2)) / Fraction(4, 1)
        velocidade_m_s = q_m3_s / area_secao_m2

        # Perda de carga unitária J (Hazen-Williams calibrado para aço carbono NBR 5580)
        # J = 700 * Q_lpm^2 / D_mm^5 [mca/m]
        j_unitario = (Fraction(700, 1) * (vazao_sprinklers_desbalanceada_l_min**2)) / Fraction(diametro_int_mm**5)
        delta_h_trecho = j_unitario * comp_total_m

        perda_carga_total_tubos += delta_h_trecho
        desnivel_total += trecho.desnivel_geometrico_m

        resultados_trechos.append(
            ResultadoTrecho(
                identificador=trecho.identificador,
                tubo_id=trecho.tubo_id,
                dn_pol=dn_pol,
                diametro_interno_mm=diametro_int_mm,
                vazao_l_min=vazao_sprinklers_desbalanceada_l_min,
                velocidade_m_s=velocidade_m_s,
                comprimento_real_m=trecho.comprimento_real_m,
                comprimento_equivalente_m=comp_eq_conexoes,
                comprimento_total_m=comp_total_m,
                perda_unitaria_mca_m=j_unitario,
                perda_carga_mca=delta_h_trecho,
                desnivel_m=trecho.desnivel_geometrico_m,
            )
        )

    # 11. Altura Manométrica Total da Bomba
    # H_man = Desnível Total + Perda de Carga em Tubulações + Pressão no Bico Crítico
    altura_manometrica_total_mca = desnivel_total + perda_carga_total_tubos + pressao_adotada_bico_mca

    # 12. Potência da moto-bomba em CV
    # Potência (cv) = (Q_total [L/min] * H_man [mca]) / (4500 * rendimento)
    potencia_bomba_cv = (vazao_total_sistema_l_min * altura_manometrica_total_mca) / (
        Fraction(4500, 1) * instalacao.rendimento_bomba
    )

    # Seleção de motor comercial padrão arredondado para cima
    potencia_comercial_cv = POTENCIAS_COMERCIAIS_CV[-1]
    for pot in POTENCIAS_COMERCIAIS_CV:
        if Fraction(pot, 1) >= potencia_bomba_cv:
            potencia_comercial_cv = pot
            break

    if not observacoes:
        observacoes.append("Instalação plenamente conforme com os requisitos da ABNT NBR 10897:2020.")

    return ResultadoDimensionamentoSprinklers(
        projeto=instalacao.projeto,
        classe_risco=instalacao.classe_risco,
        nome_classe_risco=nome_risco,
        densidade_adotada_mm_min=densidade_min_mm_min,
        area_operacao_adotada_m2=area_operacao_adotada,
        area_por_bico_m2=area_bico_m2,
        vazao_bico_critico_l_min=vazao_bico_critico_l_min,
        pressao_minima_bico_mca=pressao_adotada_bico_mca,
        fator_k=fator_k,
        numero_bicos_operacao=numero_bicos_operacao,
        vazao_bicos_l_min=vazao_bicos_l_min,
        vazao_sprinklers_desbalanceada_l_min=vazao_sprinklers_desbalanceada_l_min,
        vazao_hidrantes_adicionais_l_min=vazao_hidrantes_l_min,
        vazao_total_sistema_l_min=vazao_total_sistema_l_min,
        tempo_minimo_rti_min=tempo_rti_min,
        volume_rti_m3=volume_rti_m3,
        trechos=tuple(resultados_trechos),
        perda_carga_total_tubulacao_mca=perda_carga_total_tubos,
        desnivel_geometrico_total_m=desnivel_total,
        altura_manometrica_total_mca=altura_manometrica_total_mca,
        potencia_bomba_cv=potencia_bomba_cv,
        potencia_comercial_bomba_cv=potencia_comercial_cv,
        atende_norma=atende_norma,
        observacoes=tuple(observacoes),
    )
