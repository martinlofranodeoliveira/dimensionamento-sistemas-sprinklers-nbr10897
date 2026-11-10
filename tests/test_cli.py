"""Testes unitários para a interface de linha de comando CLI da NBR 10897:2020."""

from __future__ import annotations

from pathlib import Path
import pytest

from sprinklers_nbr10897.cli import main


def test_cli_catalogo(capsys) -> None:
    codigo = main(["catalogo"])
    assert codigo == 0
    saida = capsys.readouterr().out
    assert "CATÁLOGO NORMATIVO ABNT NBR 10897:2020" in saida
    assert "risco_leve" in saida
    assert "K80" in saida
    assert "4_pol" in saida


def test_cli_gerar_exemplo_stdout(capsys) -> None:
    codigo = main(["gerar-exemplo", "--tipo", "risco_leve"])
    assert codigo == 0
    saida = capsys.readouterr().out
    assert '"classe_risco": "risco_leve"' in saida


def test_cli_gerar_exemplo_arquivo(tmp_path) -> None:
    saida_json = tmp_path / "exemplo_gerado.json"
    codigo = main(["gerar-exemplo", "--tipo", "risco_ordinario_1", "--saida", str(saida_json)])
    assert codigo == 0
    assert saida_json.exists()
    conteudo = saida_json.read_text(encoding="utf-8")
    assert '"classe_risco": "risco_ordinario_1"' in conteudo


def test_cli_calcular_completo(tmp_path, capsys) -> None:
    ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
    out_txt = tmp_path / "relatorio.txt"
    out_json = tmp_path / "resultado.json"
    out_csv = tmp_path / "trechos.csv"
    out_svg = tmp_path / "painel.svg"
    out_zip = tmp_path / "pacote.zip"

    codigo = main([
        "calcular",
        str(ex_path),
        "--saida-txt", str(out_txt),
        "--saida-json", str(out_json),
        "--saida-csv", str(out_csv),
        "--saida-svg", str(out_svg),
        "--pacote-zip", str(out_zip),
    ])
    assert codigo == 0
    assert out_txt.exists()
    assert out_json.exists()
    assert out_csv.exists()
    assert out_svg.exists()
    assert out_zip.exists()

    saida = capsys.readouterr().out
    assert "LOFRANO TECNOLOGIA" in saida


def test_cli_calcular_arquivo_inexistente(capsys) -> None:
    codigo = main(["calcular", "arquivo_inexistente_123.json"])
    assert codigo == 1
    err = capsys.readouterr().err
    assert "não encontrado" in err
