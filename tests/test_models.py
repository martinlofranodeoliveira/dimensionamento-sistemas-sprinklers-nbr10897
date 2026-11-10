"""Testes unitários para modelos de dados de sprinklers NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
import pytest

from sprinklers_nbr10897.models import (
    BicoSprinkler,
    ConexoesTrecho,
    InstalacaoSprinklers,
    TrechoRede,
)


def test_bico_sprinkler_valido() -> None:
    bico = BicoSprinkler(
        modelo_fator_k="K80",
        espacamento_s_m=Fraction(3, 1),
        espacamento_l_m=Fraction(4, 1),
    )
    assert bico.modelo_fator_k == "K80"
    assert bico.espacamento_s_m == Fraction(3, 1)
    assert bico.espacamento_l_m == Fraction(4, 1)
    assert bico.area_cobertura_m2 == Fraction(12, 1)


def test_bico_sprinkler_espacamento_invalido() -> None:
    with pytest.raises(ValueError, match="estritamente positivos"):
        BicoSprinkler("K80", Fraction(0, 1), Fraction(3, 1))

    with pytest.raises(ValueError, match="estritamente positivos"):
        BicoSprinkler("K80", Fraction(3, 1), Fraction(-1, 1))


def test_conexoes_trecho_negativo() -> None:
    with pytest.raises(ValueError, match="não pode ser negativa"):
        ConexoesTrecho(joelho_90=-1)


def test_trecho_rede_validacoes() -> None:
    with pytest.raises(ValueError, match="não pode ser vazio"):
        TrechoRede(
            identificador="  ",
            tubo_id="3_pol",
            comprimento_real_m=Fraction(10, 1),
            desnivel_geometrico_m=Fraction(0, 1),
            conexoes=ConexoesTrecho(),
        )

    with pytest.raises(ValueError, match="não pode ser negativo"):
        TrechoRede(
            identificador="TRECHO_1",
            tubo_id="3_pol",
            comprimento_real_m=Fraction(-5, 1),
            desnivel_geometrico_m=Fraction(0, 1),
            conexoes=ConexoesTrecho(),
        )


def test_instalacao_sprinklers_validacoes() -> None:
    bico = BicoSprinkler("K80", Fraction(3, 1), Fraction(3, 1))
    trecho = TrechoRede("T1", "3_pol", Fraction(5, 1), Fraction(0, 1), ConexoesTrecho())

    with pytest.raises(ValueError, match="nome do projeto não pode ser vazio"):
        InstalacaoSprinklers(
            projeto="  ",
            classe_risco="risco_leve",
            area_compartimento_m2=Fraction(200, 1),
            bico=bico,
            trechos=(trecho,),
        )

    with pytest.raises(ValueError, match="área do compartimento deve ser estritamente positiva"):
        InstalacaoSprinklers(
            projeto="Projeto A",
            classe_risco="risco_leve",
            area_compartimento_m2=Fraction(0, 1),
            bico=bico,
            trechos=(trecho,),
        )

    with pytest.raises(ValueError, match="deve conter pelo menos um trecho"):
        InstalacaoSprinklers(
            projeto="Projeto A",
            classe_risco="risco_leve",
            area_compartimento_m2=Fraction(200, 1),
            bico=bico,
            trechos=(),
        )

    with pytest.raises(ValueError, match="margem de desbalanceamento"):
        InstalacaoSprinklers(
            projeto="Projeto A",
            classe_risco="risco_leve",
            area_compartimento_m2=Fraction(200, 1),
            bico=bico,
            trechos=(trecho,),
            margem_desbalanceamento_pct=Fraction(-5, 1),
        )

    with pytest.raises(ValueError, match="rendimento da bomba"):
        InstalacaoSprinklers(
            projeto="Projeto A",
            classe_risco="risco_leve",
            area_compartimento_m2=Fraction(200, 1),
            bico=bico,
            trechos=(trecho,),
            rendimento_bomba=Fraction(150, 100),
        )
