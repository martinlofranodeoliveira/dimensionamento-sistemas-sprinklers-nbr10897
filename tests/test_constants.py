"""Testes unitários para as constantes e tabelas normativas NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
import pytest

from sprinklers_nbr10897.constants import (
    CLASSES_RISCO_OCUPACAO,
    CONEXOES_EQUIVALENTES_SPRINKLERS_M,
    DENSIDADE_AGUA_KGF_M3,
    FATORES_K_SPRINKLERS,
    PERDA_VGA_METROS_EQUIVALENTES,
    RENDIMENTO_PADRAO_BOMBA,
    TUBOS_ACO_SPRINKLERS,
)


def test_constantes_globais() -> None:
    assert DENSIDADE_AGUA_KGF_M3 == 1000
    assert RENDIMENTO_PADRAO_BOMBA == Fraction(65, 100)


def test_classes_risco_ocupacao_presenca() -> None:
    chaves_esperadas = {
        "risco_leve",
        "risco_ordinario_1",
        "risco_ordinario_2",
        "risco_extra_1",
        "risco_extra_2",
    }
    assert set(CLASSES_RISCO_OCUPACAO.keys()) == chaves_esperadas


@pytest.mark.parametrize("chave", list(CLASSES_RISCO_OCUPACAO.keys()))
def test_classes_risco_campos_obrigatorios(chave: str) -> None:
    info = CLASSES_RISCO_OCUPACAO[chave]
    assert "codigo" in info
    assert "nome" in info
    assert isinstance(info["densidade_minima_mm_min"], Fraction)
    assert info["densidade_minima_mm_min"] > 0
    assert isinstance(info["area_operacao_minima_m2"], int)
    assert info["area_operacao_minima_m2"] > 0
    assert isinstance(info["area_maxima_bico_m2"], Fraction)
    assert info["area_maxima_bico_m2"] > 0
    assert isinstance(info["tempo_minimo_rti_min"], int)
    assert info["tempo_minimo_rti_min"] > 0
    assert isinstance(info["vazao_hidrantes_adicionais_l_min"], Fraction)
    assert info["vazao_hidrantes_adicionais_l_min"] > 0
    assert isinstance(info["pressao_minima_bico_mca"], Fraction)
    assert info["pressao_minima_bico_mca"] > 0


def test_fatores_k_sprinklers() -> None:
    modelos = {"K80", "K115", "K160", "K200"}
    assert set(FATORES_K_SPRINKLERS.keys()) == modelos
    for mod in modelos:
        info = FATORES_K_SPRINKLERS[mod]
        assert info["fator_k"] > 0
        assert isinstance(info["orificio_nominal_mm"], Fraction)
        assert info["orificio_nominal_mm"] > 0


def test_tubos_aco_sprinklers() -> None:
    assert "1_pol" in TUBOS_ACO_SPRINKLERS
    assert "4_pol" in TUBOS_ACO_SPRINKLERS
    assert "6_pol" in TUBOS_ACO_SPRINKLERS
    for k, t in TUBOS_ACO_SPRINKLERS.items():
        assert isinstance(t["diametro_interno_mm"], Fraction)
        assert t["diametro_interno_mm"] > 0
        assert t["rugosidade_c"] == 120


def test_conexoes_equivalentes() -> None:
    for tubo, conexoes in CONEXOES_EQUIVALENTES_SPRINKLERS_M.items():
        assert tubo in TUBOS_ACO_SPRINKLERS
        for c, v in conexoes.items():
            assert isinstance(v, Fraction)
            assert v > 0


def test_perda_vga() -> None:
    for tubo, perda in PERDA_VGA_METROS_EQUIVALENTES.items():
        assert tubo in TUBOS_ACO_SPRINKLERS
        assert isinstance(perda, Fraction)
        assert perda > 0
