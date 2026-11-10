"""Testes unitários para o motor de cálculo da NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
import unittest

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


class TestCalculadora(unittest.TestCase):
    def test_raiz_quadrada_frac_quadrados_perfeitos(self) -> None:
        self.assertEqual(raiz_quadrada_frac(Fraction(0, 1)), Fraction(0, 1))
        self.assertEqual(raiz_quadrada_frac(Fraction(4, 1)), Fraction(2, 1))
        self.assertEqual(raiz_quadrada_frac(Fraction(9, 16)), Fraction(3, 4))
        self.assertEqual(raiz_quadrada_frac(Fraction(100, 25)), Fraction(2, 1))

    def test_raiz_quadrada_frac_irracionais(self) -> None:
        r2 = raiz_quadrada_frac(Fraction(2, 1))
        self.assertTrue(abs(r2 - Fraction(1414213, 1000000)) < Fraction(1, 100000))
        with self.assertRaises(ValueError):
            raiz_quadrada_frac(Fraction(-4, 1))

    def test_teto_divisao_frac(self) -> None:
        self.assertEqual(teto_divisao_frac(Fraction(10, 1), Fraction(5, 1)), 2)
        self.assertEqual(teto_divisao_frac(Fraction(11, 1), Fraction(5, 1)), 3)
        self.assertEqual(teto_divisao_frac(Fraction(139, 1), Fraction(12, 1)), 12)
        with self.assertRaises(ZeroDivisionError):
            teto_divisao_frac(Fraction(10, 1), Fraction(0, 1))

    def test_calculo_risco_leve_padrao(self) -> None:
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

        self.assertEqual(res.classe_risco, "risco_leve")
        self.assertTrue(res.atende_norma)
        self.assertEqual(res.fator_k, 80)
        self.assertEqual(res.area_operacao_adotada_m2, Fraction(139, 1))
        self.assertEqual(res.numero_bicos_operacao, 12)  # ceil(139 / 12.25) = 12
        self.assertEqual(res.tempo_minimo_rti_min, 30)
        self.assertGreater(res.volume_rti_m3, 0)
        self.assertGreater(res.altura_manometrica_total_mca, 0)
        self.assertIn(res.potencia_comercial_bomba_cv, (1, 2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100))

    def test_calculo_risco_ordinario_1(self) -> None:
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
        self.assertEqual(res.classe_risco, "risco_ordinario_1")
        self.assertEqual(res.tempo_minimo_rti_min, 60)
        self.assertEqual(res.vazao_hidrantes_adicionais_l_min, Fraction(950, 1))
        self.assertTrue(res.atende_norma)

    def test_calculo_risco_ordinario_2(self) -> None:
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
        self.assertEqual(res.classe_risco, "risco_ordinario_2")
        self.assertEqual(res.densidade_adotada_mm_min, Fraction(81, 10))
        self.assertTrue(res.atende_norma)

    def test_calculo_risco_extra_1(self) -> None:
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
        self.assertEqual(res.classe_risco, "risco_extra_1")
        self.assertEqual(res.tempo_minimo_rti_min, 90)
        self.assertGreaterEqual(res.pressao_minima_bico_mca, Fraction(7, 1))
        self.assertTrue(res.atende_norma)

    def test_calculo_risco_extra_2(self) -> None:
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
        self.assertEqual(res.classe_risco, "risco_extra_2")
        self.assertEqual(res.densidade_adotada_mm_min, Fraction(163, 10))
        self.assertEqual(res.tempo_minimo_rti_min, 120)
        self.assertTrue(res.atende_norma)

    def test_area_cobertura_excedida_alerta(self) -> None:
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
        self.assertFalse(res.atende_norma)
        self.assertTrue(any("supera o limite normativo" in obs for obs in res.observacoes))

    def test_calculo_area_compartimento_menor_que_area_operacao(self) -> None:
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
        self.assertEqual(res.area_operacao_adotada_m2, Fraction(80, 1))
        self.assertTrue(any("menor que a área de operação normativa" in obs for obs in res.observacoes))

    def test_classe_risco_invalida(self) -> None:
        bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(3, 1))
        trecho = TrechoRede("T1", "3_pol", Fraction(10, 1), Fraction(0, 1), ConexoesTrecho())
        inst = InstalacaoSprinklers("Proj", "risco_inexistente", Fraction(200, 1), bico, (trecho,))
        with self.assertRaises(ValueError):
            calcular_sprinklers_nbr10897(inst)

    def test_bico_invalido(self) -> None:
        bico = BicoSprinkler("K999", Fraction(3, 1), Fraction(3, 1))
        trecho = TrechoRede("T1", "3_pol", Fraction(10, 1), Fraction(0, 1), ConexoesTrecho())
        inst = InstalacaoSprinklers("Proj", "risco_leve", Fraction(200, 1), bico, (trecho,))
        with self.assertRaises(ValueError):
            calcular_sprinklers_nbr10897(inst)

    def test_tubo_invalido(self) -> None:
        bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(3, 1))
        trecho = TrechoRede("T1", "tubo_inexistente", Fraction(10, 1), Fraction(0, 1), ConexoesTrecho())
        inst = InstalacaoSprinklers("Proj", "risco_leve", Fraction(200, 1), bico, (trecho,))
        with self.assertRaises(ValueError):
            calcular_sprinklers_nbr10897(inst)
