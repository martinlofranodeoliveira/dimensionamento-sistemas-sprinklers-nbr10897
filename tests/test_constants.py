"""Testes unitários para as constantes e tabelas normativas NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
import unittest

from sprinklers_nbr10897.constants import (
    CLASSES_RISCO_OCUPACAO,
    CONEXOES_EQUIVALENTES_SPRINKLERS_M,
    DENSIDADE_AGUA_KGF_M3,
    FATORES_K_SPRINKLERS,
    PERDA_VGA_METROS_EQUIVALENTES,
    RENDIMENTO_PADRAO_BOMBA,
    TUBOS_ACO_SPRINKLERS,
)


class TestConstantes(unittest.TestCase):
    def test_constantes_globais(self) -> None:
        self.assertEqual(DENSIDADE_AGUA_KGF_M3, 1000)
        self.assertEqual(RENDIMENTO_PADRAO_BOMBA, Fraction(65, 100))

    def test_classes_risco_ocupacao_presenca(self) -> None:
        chaves_esperadas = {
            "risco_leve",
            "risco_ordinario_1",
            "risco_ordinario_2",
            "risco_extra_1",
            "risco_extra_2",
        }
        self.assertEqual(set(CLASSES_RISCO_OCUPACAO.keys()), chaves_esperadas)

    def test_classes_risco_campos_obrigatorios(self) -> None:
        for chave, info in CLASSES_RISCO_OCUPACAO.items():
            with self.subTest(chave=chave):
                self.assertIn("codigo", info)
                self.assertIn("nome", info)
                self.assertIsInstance(info["densidade_minima_mm_min"], Fraction)
                self.assertGreater(info["densidade_minima_mm_min"], 0)
                self.assertIsInstance(info["area_operacao_minima_m2"], int)
                self.assertGreater(info["area_operacao_minima_m2"], 0)
                self.assertIsInstance(info["area_maxima_bico_m2"], Fraction)
                self.assertGreater(info["area_maxima_bico_m2"], 0)
                self.assertIsInstance(info["tempo_minimo_rti_min"], int)
                self.assertGreater(info["tempo_minimo_rti_min"], 0)
                self.assertIsInstance(info["vazao_hidrantes_adicionais_l_min"], Fraction)
                self.assertGreater(info["vazao_hidrantes_adicionais_l_min"], 0)
                self.assertIsInstance(info["pressao_minima_bico_mca"], Fraction)
                self.assertGreater(info["pressao_minima_bico_mca"], 0)

    def test_fatores_k_sprinklers(self) -> None:
        modelos = {"K80", "K115", "K160", "K200"}
        self.assertEqual(set(FATORES_K_SPRINKLERS.keys()), modelos)
        for mod in modelos:
            with self.subTest(modelo=mod):
                info = FATORES_K_SPRINKLERS[mod]
                self.assertGreater(info["fator_k"], 0)
                self.assertIsInstance(info["orificio_nominal_mm"], Fraction)
                self.assertGreater(info["orificio_nominal_mm"], 0)

    def test_tubos_aco_sprinklers(self) -> None:
        self.assertIn("1_pol", TUBOS_ACO_SPRINKLERS)
        self.assertIn("4_pol", TUBOS_ACO_SPRINKLERS)
        self.assertIn("6_pol", TUBOS_ACO_SPRINKLERS)
        for k, t in TUBOS_ACO_SPRINKLERS.items():
            with self.subTest(tubo=k):
                self.assertIsInstance(t["diametro_interno_mm"], Fraction)
                self.assertGreater(t["diametro_interno_mm"], 0)
                self.assertEqual(t["rugosidade_c"], 120)

    def test_conexoes_equivalentes(self) -> None:
        for tubo, conexoes in CONEXOES_EQUIVALENTES_SPRINKLERS_M.items():
            with self.subTest(tubo=tubo):
                self.assertIn(tubo, TUBOS_ACO_SPRINKLERS)
                for c, v in conexoes.items():
                    self.assertIsInstance(v, Fraction)
                    self.assertGreater(v, 0)

    def test_perda_vga(self) -> None:
        for tubo, perda in PERDA_VGA_METROS_EQUIVALENTES.items():
            with self.subTest(tubo=tubo):
                self.assertIn(tubo, TUBOS_ACO_SPRINKLERS)
                self.assertIsInstance(perda, Fraction)
                self.assertGreater(perda, 0)
