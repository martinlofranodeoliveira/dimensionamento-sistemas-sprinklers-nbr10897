"""Testes unitários para os exportadores TXT, CSV e ZIP da NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from sprinklers_nbr10897.calculator import calcular_sprinklers_nbr10897
from sprinklers_nbr10897.codecs import decodificar_instalacao_json
from sprinklers_nbr10897.exporters import (
    DATA_FIXA_ZIP,
    criar_pacote_zip_deterministico,
    formatar_fracao_decimal,
    gerar_csv_trechos,
    gerar_relatorio_texto,
    sanitizar_campo_csv,
)


class TestExportadores(unittest.TestCase):
    def setUp(self) -> None:
        ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
        inst = decodificar_instalacao_json(ex_path.read_text(encoding="utf-8"))
        self.resultado = calcular_sprinklers_nbr10897(inst)
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_formatar_fracao_decimal(self) -> None:
        self.assertEqual(formatar_fracao_decimal(Fraction(0, 1)), "0,00")
        self.assertEqual(formatar_fracao_decimal(Fraction(10, 1)), "10,00")
        self.assertEqual(formatar_fracao_decimal(Fraction(41, 10)), "4,10")
        self.assertEqual(formatar_fracao_decimal(Fraction(1, 3), casas=4), "0,3333")
        self.assertEqual(formatar_fracao_decimal(Fraction(-15, 2)), "-7,50")

    def test_sanitizar_campo_csv(self) -> None:
        self.assertEqual(sanitizar_campo_csv("normal"), "normal")
        self.assertEqual(sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(sanitizar_campo_csv("+SOMA()"), "'+SOMA()")
        self.assertEqual(sanitizar_campo_csv("-10"), "'-10")
        self.assertEqual(sanitizar_campo_csv("@CMD"), "'@CMD")
        self.assertEqual(sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(sanitizar_campo_csv("\rret"), "'\rret")

    def test_gerar_relatorio_texto(self) -> None:
        texto = gerar_relatorio_texto(self.resultado)
        self.assertIn("LOFRANO TECNOLOGIA", texto)
        self.assertIn("ABNT NBR 10897:2020", texto)
        self.assertIn("RTI", texto)
        self.assertIn("MOTO-BOMBA PRINCIPAL", texto)
        self.assertIn("CONFORME", texto)

    def test_gerar_csv_trechos(self) -> None:
        csv_str = gerar_csv_trechos(self.resultado)
        linhas = csv_str.strip().split("\n")
        self.assertGreaterEqual(len(linhas), 2)
        self.assertIn("identificador;tubo_id;dn_pol", linhas[0])
        self.assertIn("SUCCAO_BOMBA", csv_str)

    def test_criar_pacote_zip_deterministico(self) -> None:
        zip_path = self.temp_dir / "teste_pacote.zip"
        caminho_gerado = criar_pacote_zip_deterministico(
            zip_path,
            self.resultado,
            conteudo_svg="<svg></svg>",
            sobrescrever=True,
        )
        self.assertTrue(caminho_gerado.exists())
        self.assertGreater(zip_path.stat().st_size, 0)

        with zipfile.ZipFile(zip_path, "r") as zf:
            nomes = zf.namelist()
            self.assertIn("relatorio_tecnico.txt", nomes)
            self.assertIn("resultado.json", nomes)
            self.assertIn("trechos.csv", nomes)
            self.assertIn("painel_sistema.svg", nomes)

            for info in zf.infolist():
                self.assertEqual(info.date_time, DATA_FIXA_ZIP)

        with self.assertRaises(FileExistsError):
            criar_pacote_zip_deterministico(zip_path, self.resultado, sobrescrever=False)
