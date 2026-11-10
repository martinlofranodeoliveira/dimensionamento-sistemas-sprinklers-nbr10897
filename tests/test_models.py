"""Testes unitários para modelos de dados de sprinklers NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
import unittest

from sprinklers_nbr10897.models import (
    BicoSprinkler,
    ConexoesTrecho,
    InstalacaoSprinklers,
    TrechoRede,
)


class TestModelos(unittest.TestCase):
    def test_bico_sprinkler_valido(self) -> None:
        bico = BicoSprinkler(
            modelo_fator_k="K80",
            espacamento_s_m=Fraction(3, 1),
            espacamento_l_m=Fraction(4, 1),
        )
        self.assertEqual(bico.modelo_fator_k, "K80")
        self.assertEqual(bico.espacamento_s_m, Fraction(3, 1))
        self.assertEqual(bico.espacamento_l_m, Fraction(4, 1))
        self.assertEqual(bico.area_cobertura_m2, Fraction(12, 1))

    def test_bico_sprinkler_espacamento_invalido(self) -> None:
        with self.assertRaises(ValueError):
            BicoSprinkler("K80", Fraction(0, 1), Fraction(3, 1))

        with self.assertRaises(ValueError):
            BicoSprinkler("K80", Fraction(3, 1), Fraction(-1, 1))

    def test_conexoes_trecho_negativo(self) -> None:
        with self.assertRaises(ValueError):
            ConexoesTrecho(joelho_90=-1)

    def test_trecho_rede_validacoes(self) -> None:
        with self.assertRaises(ValueError):
            TrechoRede(
                identificador="  ",
                tubo_id="3_pol",
                comprimento_real_m=Fraction(10, 1),
                desnivel_geometrico_m=Fraction(0, 1),
                conexoes=ConexoesTrecho(),
            )

        with self.assertRaises(ValueError):
            TrechoRede(
                identificador="TRECHO_1",
                tubo_id="3_pol",
                comprimento_real_m=Fraction(-5, 1),
                desnivel_geometrico_m=Fraction(0, 1),
                conexoes=ConexoesTrecho(),
            )

    def test_instalacao_sprinklers_validacoes(self) -> None:
        bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(3, 1))
        trecho = TrechoRede("T1", "3_pol", Fraction(5, 1), Fraction(0, 1), ConexoesTrecho())

        with self.assertRaises(ValueError):
            InstalacaoSprinklers(
                projeto="  ",
                classe_risco="risco_leve",
                area_compartimento_m2=Fraction(200, 1),
                bico=bico,
                trechos=(trecho,),
            )

        with self.assertRaises(ValueError):
            InstalacaoSprinklers(
                projeto="Projeto A",
                classe_risco="risco_leve",
                area_compartimento_m2=Fraction(0, 1),
                bico=bico,
                trechos=(trecho,),
            )

        with self.assertRaises(ValueError):
            InstalacaoSprinklers(
                projeto="Projeto A",
                classe_risco="risco_leve",
                area_compartimento_m2=Fraction(200, 1),
                bico=bico,
                trechos=(),
            )

        with self.assertRaises(ValueError):
            InstalacaoSprinklers(
                projeto="Projeto A",
                classe_risco="risco_leve",
                area_compartimento_m2=Fraction(200, 1),
                bico=bico,
                trechos=(trecho,),
                margem_desbalanceamento_pct=Fraction(-5, 1),
            )

        with self.assertRaises(ValueError):
            InstalacaoSprinklers(
                projeto="Projeto A",
                classe_risco="risco_leve",
                area_compartimento_m2=Fraction(200, 1),
                bico=bico,
                trechos=(trecho,),
                rendimento_bomba=Fraction(150, 100),
            )
