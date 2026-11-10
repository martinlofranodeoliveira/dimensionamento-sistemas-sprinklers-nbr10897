"""Testes unitários para o gerador de painel SVG 1440x900 da NBR 10897:2020."""

from __future__ import annotations

from pathlib import Path
import unittest

from sprinklers_nbr10897.calculator import calcular_sprinklers_nbr10897
from sprinklers_nbr10897.codecs import decodificar_instalacao_json
from sprinklers_nbr10897.svg_generator import gerar_painel_svg


class TestSvgGenerator(unittest.TestCase):
    def setUp(self) -> None:
        ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
        inst = decodificar_instalacao_json(ex_path.read_text(encoding="utf-8"))
        self.resultado = calcular_sprinklers_nbr10897(inst)

    def test_gerar_painel_svg_estrutura(self) -> None:
        svg = gerar_painel_svg(self.resultado)
        self.assertIn('<svg xmlns="http://www.w3.org/2000/svg"', svg)
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn('width="1440"', svg)
        self.assertIn('height="900"', svg)
        self.assertIn("</svg>", svg)

    def test_gerar_painel_svg_elementos_tecnicos(self) -> None:
        svg = gerar_painel_svg(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("ABNT NBR 10897:2020", svg)
        self.assertIn("VAZÃO TOTAL DO SISTEMA", svg)
        self.assertIn("BICOS EM OPERAÇÃO", svg)
        self.assertIn("RESERVA TÉCNICA (RTI)", svg)
        self.assertIn("ALTURA MANOMÉTRICA (Hman)", svg)
        self.assertIn("MOTO-BOMBA PRINCIPAL", svg)
        self.assertIn("VGA", svg)
        self.assertIn("BICO CRÍTICO", svg)
