"""Testes unitários para codecs e validações RFC 8259 da NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import pytest

from sprinklers_nbr10897.calculator import calcular_sprinklers_nbr10897
from sprinklers_nbr10897.codecs import (
    codificar_resultado_json,
    decodificar_instalacao_json,
    instalacao_para_dict,
    parse_fracao_ou_int,
    resultado_para_dict,
)


def test_parse_fracao_ou_int_validos() -> None:
    assert parse_fracao_ou_int(10, "campo") == Fraction(10, 1)
    assert parse_fracao_ou_int("41/10", "campo") == Fraction(41, 10)
    assert parse_fracao_ou_int("4.1", "campo") == Fraction(41, 10)


def test_parse_fracao_ou_int_rejeita_float() -> None:
    with pytest.raises(TypeError, match="ponto flutuante float proibido"):
        parse_fracao_ou_int(4.1, "campo")


def test_parse_fracao_ou_int_rejeita_vazio_e_invalido() -> None:
    with pytest.raises(ValueError, match="não pode ser string vazia"):
        parse_fracao_ou_int("   ", "campo")

    with pytest.raises(ValueError, match="inválido"):
        parse_fracao_ou_int("abc", "campo")

    with pytest.raises(TypeError, match="Tipo inválido"):
        parse_fracao_ou_int([], "campo")


def test_decodificacao_exemplos_reais() -> None:
    ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
    conteudo = ex_path.read_text(encoding="utf-8")
    inst = decodificar_instalacao_json(conteudo)
    assert inst.projeto == "Edifício Corporativo Paulista - Pavimento Tipo"
    assert inst.classe_risco == "risco_leve"
    assert len(inst.trechos) == 4


def test_decodificacao_bytes_utf8() -> None:
    ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
    conteudo_bytes = ex_path.read_bytes()
    inst = decodificar_instalacao_json(conteudo_bytes)
    assert inst.classe_risco == "risco_leve"


def test_rejeicao_bom_utf8() -> None:
    with pytest.raises(ValueError, match="BOM UTF-8 proibido"):
        decodificar_instalacao_json("\ufeff{}")

    with pytest.raises(ValueError, match="BOM UTF-8 proibido"):
        decodificar_instalacao_json(b"\xef\xbb\xbf{}")


def test_rejeicao_chave_duplicada() -> None:
    json_dup = '{"projeto": "A", "projeto": "B", "classe_risco": "risco_leve"}'
    with pytest.raises(ValueError, match="Chave duplicada"):
        decodificar_instalacao_json(json_dup)


def test_rejeicao_float_nativo_no_json() -> None:
    # Float puro sem aspas deve ser bloqueado pelo parse_float
    json_float = '{"projeto": "A", "area_compartimento_m2": 500.5}'
    with pytest.raises(TypeError, match="proibido"):
        decodificar_instalacao_json(json_float)


def test_rejeicao_profundidade_excessiva() -> None:
    # Cria json com 35 níveis
    profundo: dict = {"nivel": 0}
    atual = profundo
    for i in range(1, 35):
        atual["prox"] = {"nivel": i}
        atual = atual["prox"]

    import json
    texto_profundo = json.dumps(profundo)
    with pytest.raises(ValueError, match="Profundidade de aninhamento"):
        decodificar_instalacao_json(texto_profundo)


def test_serializacao_e_roundtrip() -> None:
    ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
    inst = decodificar_instalacao_json(ex_path.read_text(encoding="utf-8"))
    res = calcular_sprinklers_nbr10897(inst)

    dict_inst = instalacao_para_dict(inst)
    assert dict_inst["classe_risco"] == "risco_leve"

    dict_res = resultado_para_dict(res)
    assert dict_res["fator_k"] == 80

    json_str = codificar_resultado_json(res)
    assert "LOFRANO" not in json_str  # JSON canônico estruturado
    assert '"fator_k": 80' in json_str
