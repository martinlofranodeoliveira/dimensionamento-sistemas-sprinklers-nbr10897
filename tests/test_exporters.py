"""Testes unitários para os exportadores TXT, CSV e ZIP da NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import zipfile
import pytest

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


@pytest.fixture
def resultado_exemplo():
    ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
    inst = decodificar_instalacao_json(ex_path.read_text(encoding="utf-8"))
    return calcular_sprinklers_nbr10897(inst)


def test_formatar_fracao_decimal() -> None:
    assert formatar_fracao_decimal(Fraction(0, 1)) == "0,00"
    assert formatar_fracao_decimal(Fraction(10, 1)) == "10,00"
    assert formatar_fracao_decimal(Fraction(41, 10)) == "4,10"
    assert formatar_fracao_decimal(Fraction(1, 3), casas=4) == "0,3333"
    assert formatar_fracao_decimal(Fraction(-15, 2)) == "-7,50"


def test_sanitizar_campo_csv() -> None:
    assert sanitizar_campo_csv("normal") == "normal"
    assert sanitizar_campo_csv("=1+1") == "'=1+1"
    assert sanitizar_campo_csv("+SOMA()") == "'+SOMA()"
    assert sanitizar_campo_csv("-10") == "'-10"
    assert sanitizar_campo_csv("@CMD") == "'@CMD"
    assert sanitizar_campo_csv("\ttab") == "'\ttab"
    assert sanitizar_campo_csv("\rret") == "'\rret"


def test_gerar_relatorio_texto(resultado_exemplo) -> None:
    texto = gerar_relatorio_texto(resultado_exemplo)
    assert "LOFRANO TECNOLOGIA" in texto
    assert "ABNT NBR 10897:2020" in texto
    assert "RTI" in texto
    assert "MOTO-BOMBA PRINCIPAL" in texto
    assert "CONFORME" in texto


def test_gerar_csv_trechos(resultado_exemplo) -> None:
    csv_str = gerar_csv_trechos(resultado_exemplo)
    linhas = csv_str.strip().split("\n")
    assert len(linhas) >= 2
    assert "identificador;tubo_id;dn_pol" in linhas[0]
    assert "SUCCAO_BOMBA" in csv_str


def test_criar_pacote_zip_deterministico(resultado_exemplo, tmp_path) -> None:
    zip_path = tmp_path / "teste_pacote.zip"
    caminho_gerado = criar_pacote_zip_deterministico(
        zip_path,
        resultado_exemplo,
        conteudo_svg="<svg></svg>",
        sobrescrever=True,
    )
    assert caminho_gerado.exists()
    assert zip_path.stat().st_size > 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        nomes = zf.namelist()
        assert "relatorio_tecnico.txt" in nomes
        assert "resultado.json" in nomes
        assert "trechos.csv" in nomes
        assert "painel_sistema.svg" in nomes

        for info in zf.infolist():
            assert info.date_time == DATA_FIXA_ZIP

    # Teste de recusa de sobrescrita com sobrescrever=False
    with pytest.raises(FileExistsError, match="já existe"):
        criar_pacote_zip_deterministico(zip_path, resultado_exemplo, sobrescrever=False)
