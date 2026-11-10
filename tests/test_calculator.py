"""Testes unitários para o motor de cálculo da NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
import pytest

from sprinklers_nbr10897.calculator import (
    calcular_sprinklers_nbr10897,
    raiz_quadrada_frac,
    teto_divisao_frac,
)
from sprinklers_nbr10897.models import (
    BicoSprinkler,
    ConexoesTrecho,
    InstalacaoSprinklers,
    TrechoRede,
)


def test_raiz_quadrada_frac_quadrados_perfeitos() -> None:
    assert raiz_quadrada_frac(Fraction(0, 1)) == Fraction(0, 1)
    assert raiz_quadrada_frac(Fraction(4, 1)) == Fraction(2, 1)
    assert raiz_quadrada_frac(Fraction(9, 16)) == Fraction(3, 4)
    assert raiz_quadrada_frac(Fraction(100, 25)) == Fraction(2, 1)


def test_raiz_quadrada_frac_irracionais() -> None:
    r2 = raiz_quadrada_frac(Fraction(2, 1))
    # r2 deve estar muito próximo de 1.414213
    assert abs(r2 - Fraction(1414213, 1000000)) < Fraction(1, 100000)

    # raiz de fração negativa deve falhar
    with pytest.raises(ValueError, match="negativa"):
        raiz_quadrada_frac(Fraction(-4, 1))


def test_teto_divisao_frac() -> None:
    assert teto_divisao_frac(Fraction(10, 1), Fraction(5, 1)) == 2
    assert teto_divisao_frac(Fraction(11, 1), Fraction(5, 1)) == 3
    assert teto_divisao_frac(Fraction(139, 1), Fraction(12, 1)) == 12
    with pytest.raises(ZeroDivisionError):
        teto_divisao_frac(Fraction(10, 1), Fraction(0, 1))


def test_calculo_risco_leve_padrao() -> None:
    bico = BicoSprinkler("K80", Fraction(35, 10), Fraction(35, 10))  # 12,25 m²
    trecho = TrechoRede(
        identificador="BARRILETE",
        tubo_id="2_1_2_pol",
        comprimento_real_m=Fraction(20, 1),
        desnivel_geometrico_m=Fraction(5, 1),
        conexoes=ConexoesTrecho(joelho_90=2, valvula_gaveta=1),
        tem_vga=True,
    )
    inst = InstalacaoSprinklers(
        projeto="Edifício Teste RL",
        classe_risco="risco_leve",
        area_compartimento_m2=Fraction(500, 1),
        bico=bico,
        trechos=(trecho,),
    )
    res = calcular_sprinklers_nbr10897(inst)

    assert res.classe_risco == "risco_leve"
    assert res.atende_norma is True
    assert res.fator_k == 80
    assert res.area_operacao_adotada_m2 == Fraction(139, 1)
    assert res.numero_bicos_operacao == 12  # ceil(139 / 12.25) = 12
    assert res.tempo_minimo_rti_min == 30
    assert res.volume_rti_m3 > 0
    assert res.altura_manometrica_total_mca > 0
    assert res.potencia_comercial_bomba_cv in (1, 2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100)


def test_calculo_risco_ordinario_1() -> None:
    bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(35, 10))  # 10,5 m²
    trecho = TrechoRede("T1", "3_pol", Fraction(15, 1), Fraction(10, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers(
        projeto="Shopping Teste",
        classe_risco="risco_ordinario_1",
        area_compartimento_m2=Fraction(800, 1),
        bico=bico,
        trechos=(trecho,),
    )
    res = calcular_sprinklers_nbr10897(inst)
    assert res.classe_risco == "risco_ordinario_1"
    assert res.tempo_minimo_rti_min == 60
    assert res.vazao_hidrantes_adicionais_l_min == Fraction(950, 1)
    assert res.atende_norma is True


def test_calculo_risco_extra_1() -> None:
    bico = BicoSprinkler("K160", Fraction(28, 10), Fraction(3, 1))  # 8,4 m²
    trecho = TrechoRede("T1", "4_pol", Fraction(25, 1), Fraction(12, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers(
        projeto="Galpão Químico Teste",
        classe_risco="risco_extra_1",
        area_compartimento_m2=Fraction(1500, 1),
        bico=bico,
        trechos=(trecho,),
    )
    res = calcular_sprinklers_nbr10897(inst)
    assert res.classe_risco == "risco_extra_1"
    assert res.tempo_minimo_rti_min == 90
    assert res.pressao_minima_bico_mca >= Fraction(7, 1)
    assert res.atende_norma is True


def test_area_cobertura_excedida_alerta() -> None:
    # No Risco Extra 1 o limite é 9,0 m². Se colocarmos 4x3 = 12 m², deve alertar e marcar atende_norma=False
    bico = BicoSprinkler("K160", Fraction(4, 1), Fraction(3, 1))
    trecho = TrechoRede("T1", "4_pol", Fraction(10, 1), Fraction(0, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers(
        projeto="Galpão Excedido",
        classe_risco="risco_extra_1",
        area_compartimento_m2=Fraction(500, 1),
        bico=bico,
        trechos=(trecho,),
    )
    res = calcular_sprinklers_nbr10897(inst)
    assert res.atende_norma is False
    assert any("supera o limite normativo" in obs for obs in res.observacoes)


def test_classe_risco_invalida() -> None:
    bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(3, 1))
    trecho = TrechoRede("T1", "3_pol", Fraction(10, 1), Fraction(0, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers("Proj", "risco_inexistente", Fraction(200, 1), bico, (trecho,))
    with pytest.raises(ValueError, match="inválida"):
        calcular_sprinklers_nbr10897(inst)


def test_bico_invalido() -> None:
    bico = BicoSprinkler("K999", Fraction(3, 1), Fraction(3, 1))
    trecho = TrechoRede("T1", "3_pol", Fraction(10, 1), Fraction(0, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers("Proj", "risco_leve", Fraction(200, 1), bico, (trecho,))
    with pytest.raises(ValueError, match="inválido"):
        calcular_sprinklers_nbr10897(inst)


def test_tubo_invalido() -> None:
    bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(3, 1))
    trecho = TrechoRede("T1", "tubo_inexistente", Fraction(10, 1), Fraction(0, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers("Proj", "risco_leve", Fraction(200, 1), bico, (trecho,))
    with pytest.raises(ValueError, match="inválido"):
        calcular_sprinklers_nbr10897(inst)


def test_calculo_risco_ordinario_2() -> None:
    bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(35, 10))
    trecho = TrechoRede("T1", "3_pol", Fraction(15, 1), Fraction(5, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers(
        projeto="Depósito Leve",
        classe_risco="risco_ordinario_2",
        area_compartimento_m2=Fraction(600, 1),
        bico=bico,
        trechos=(trecho,),
    )
    res = calcular_sprinklers_nbr10897(inst)
    assert res.classe_risco == "risco_ordinario_2"
    assert res.densidade_adotada_mm_min == Fraction(81, 10)
    assert res.atende_norma is True


def test_calculo_risco_extra_2() -> None:
    bico = BicoSprinkler("K200", Fraction(25, 10), Fraction(3, 1))
    trecho = TrechoRede("T1", "6_pol", Fraction(20, 1), Fraction(10, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers(
        projeto="Armazém de Tintas e Plásticos",
        classe_risco="risco_extra_2",
        area_compartimento_m2=Fraction(2000, 1),
        bico=bico,
        trechos=(trecho,),
    )
    res = calcular_sprinklers_nbr10897(inst)
    assert res.classe_risco == "risco_extra_2"
    assert res.densidade_adotada_mm_min == Fraction(163, 10)
    assert res.tempo_minimo_rti_min == 120
    assert res.atende_norma is True


def test_calculo_area_compartimento_menor_que_area_operacao() -> None:
    # Quando o compartimento é menor que 139 m²
    bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(3, 1))
    trecho = TrechoRede("T1", "2_1_2_pol", Fraction(10, 1), Fraction(2, 1), ConexoesTrecho())
    inst = InstalacaoSprinklers(
        projeto="Sala Pequena",
        classe_risco="risco_leve",
        area_compartimento_m2=Fraction(80, 1),
        bico=bico,
        trechos=(trecho,),
    )
    res = calcular_sprinklers_nbr10897(inst)
    assert res.area_operacao_adotada_m2 == Fraction(80, 1)
    assert any("menor que a área de operação normativa" in obs for obs in res.observacoes)

