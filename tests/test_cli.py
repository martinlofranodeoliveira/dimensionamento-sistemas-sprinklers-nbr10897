"""Testes unitários para a interface de linha de comando CLI da NBR 10897:2020."""

from __future__ import annotations

import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from sprinklers_nbr10897.cli import main


class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_versao(self) -> None:
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            with self.assertRaises(SystemExit) as cm:
                main(["--versao"])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("sprinklers-nbr10897", buffer.getvalue())
        finally:
            sys.stdout = old_stdout

    def test_cli_catalogo(self) -> None:
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            codigo = main(["catalogo"])
            self.assertEqual(codigo, 0)
            saida = buffer.getvalue()
            self.assertIn("CATÁLOGO NORMATIVO ABNT NBR 10897:2020", saida)
            self.assertIn("risco_leve", saida)
            self.assertIn("K80", saida)
            self.assertIn("4_pol", saida)
        finally:
            sys.stdout = old_stdout

    def test_cli_gerar_exemplo_stdout(self) -> None:
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            codigo = main(["gerar-exemplo", "--tipo", "risco-leve"])
            self.assertEqual(codigo, 0)
            saida = buffer.getvalue()
            self.assertIn('"classe_risco": "risco_leve"', saida)
        finally:
            sys.stdout = old_stdout

    def test_cli_gerar_exemplo_arquivo(self) -> None:
        saida_json = self.temp_dir / "exemplo_gerado.json"
        codigo = main(["gerar-exemplo", "--tipo", "risco_ordinario_1", "--saida", str(saida_json)])
        self.assertEqual(codigo, 0)
        self.assertTrue(saida_json.exists())
        conteudo = saida_json.read_text(encoding="utf-8")
        self.assertIn('"classe_risco": "risco_ordinario_1"', conteudo)

    def test_cli_calcular_completo(self) -> None:
        ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
        out_txt = self.temp_dir / "relatorio.txt"
        out_json = self.temp_dir / "resultado.json"
        out_csv = self.temp_dir / "trechos.csv"
        out_svg = self.temp_dir / "painel.svg"
        out_zip = self.temp_dir / "pacote.zip"

        codigo = main([
            "calcular",
            str(ex_path),
            "--saida-txt", str(out_txt),
            "--saida-json", str(out_json),
            "--saida-csv", str(out_csv),
            "--saida-svg", str(out_svg),
            "--pacote-zip", str(out_zip),
        ])
        self.assertEqual(codigo, 0)
        self.assertTrue(out_txt.exists())
        self.assertTrue(out_json.exists())
        self.assertTrue(out_csv.exists())
        self.assertTrue(out_svg.exists())
        self.assertTrue(out_zip.exists())

    def test_cli_calcular_formato_texto(self) -> None:
        ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
        buffer = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buffer
            codigo = main(["calcular", str(ex_path), "--formato", "texto"])
            self.assertEqual(codigo, 0)
            self.assertIn("LOFRANO TECNOLOGIA", buffer.getvalue())
        finally:
            sys.stdout = old_stdout

    def test_cli_calcular_arquivo_inexistente(self) -> None:
        buffer_err = io.StringIO()
        old_stderr = sys.stderr
        try:
            sys.stderr = buffer_err
            codigo = main(["calcular", "arquivo_inexistente_123.json"])
            self.assertEqual(codigo, 1)
            self.assertIn("não encontrado", buffer_err.getvalue())
        finally:
            sys.stderr = old_stderr
