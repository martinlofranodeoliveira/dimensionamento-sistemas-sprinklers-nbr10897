"""Testes unitários para o gerador de painel SVG 1440x900 da NBR 10897:2020."""

from __future__ import annotations

from pathlib import Path
import pytest

from sprinklers_nbr10897.calculator import calcular_sprinklers_nbr10897
from sprinklers_nbr10897.codecs import decodificar_instalacao_json
from sprinklers_nbr10897.svg_generator import gerar_painel_svg


@pytest.fixture
def resultado_exemplo():
    ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
    inst = decodificar_instalacao_json(ex_path.read_text(encoding="utf-8"))
    return calcular_sprinklers_nbr10897(inst)


def test_gerar_painel_svg_estrutura(resultado_exemplo) -> None:
    svg = gerar_painel_svg(resultado_exemplo)
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in svg
    assert 'viewBox="0 0 1440 900"' in svg
    assert 'width="1440"' in svg
    assert 'height="900"' in svg
    assert "</svg>" in svg


def test_gerar_painel_svg_elementos_tecnicos(resultado_exemplo) -> None:
    svg = gerar_painel_svg(resultado_exemplo)
    assert "LOFRANO TECNOLOGIA" in svg
    assert "ABNT NBR 10897:2020" in svg
    assert "VAZÃO TOTAL DO SISTEMA" in svg
    assert "BICOS EM OPERAÇÃO" in svg
    assert "RESERVA TÉCNICA (RTI)" in svg
    assert "ALTURA MANOMÉTRICA (Hman)" in svg
    assert "MOTO-BOMBA PRINCIPAL" in svg
    assert "VGA" in svg
    assert "BICO CRÍTICO" in svg
