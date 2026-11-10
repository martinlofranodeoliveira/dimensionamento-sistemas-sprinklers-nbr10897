"""Testes unitários para codecs e validações RFC 8259 da NBR 10897:2020."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import unittest

from sprinklers_nbr10897.calculator import calcular_sprinklers_nbr10897
from sprinklers_nbr10897.codecs import (
    codificar_resultado_json,
    decodificar_instalacao_json,
    instalacao_para_dict,
    parse_fracao_ou_int,
    resultado_para_dict,
)


class TestCodecs(unittest.TestCase):
    def test_parse_fracao_ou_int_validos(self) -> None:
        self.assertEqual(parse_fracao_ou_int(10, "campo"), Fraction(10, 1))
        self.assertEqual(parse_fracao_ou_int("41/10", "campo"), Fraction(41, 10))
        self.assertEqual(parse_fracao_ou_int("4.1", "campo"), Fraction(41, 10))

    def test_parse_fracao_ou_int_rejeita_float(self) -> None:
        with self.assertRaises(TypeError):
            parse_fracao_ou_int(4.1, "campo")

    def test_parse_fracao_ou_int_rejeita_vazio_e_invalido(self) -> None:
        with self.assertRaises(ValueError):
            parse_fracao_ou_int("   ", "campo")

        with self.assertRaises(ValueError):
            parse_fracao_ou_int("abc", "campo")

        with self.assertRaises(TypeError):
            parse_fracao_ou_int([], "campo")

    def test_decodificacao_exemplos_reais(self) -> None:
        ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
        conteudo = ex_path.read_text(encoding="utf-8")
        inst = decodificar_instalacao_json(conteudo)
        self.assertEqual(inst.projeto, "Edifício Corporativo Paulista - Pavimento Tipo")
        self.assertEqual(inst.classe_risco, "risco_leve")
        self.assertEqual(len(inst.trechos), 4)

    def test_decodificacao_bytes_utf8(self) -> None:
        ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
        conteudo_bytes = ex_path.read_bytes()
        inst = decodificar_instalacao_json(conteudo_bytes)
        self.assertEqual(inst.classe_risco, "risco_leve")

    def test_rejeicao_bom_utf8(self) -> None:
        with self.assertRaises(ValueError):
            decodificar_instalacao_json("\ufeff{}")

        with self.assertRaises(ValueError):
            decodificar_instalacao_json(b"\xef\xbb\xbf{}")

    def test_rejeicao_chave_duplicada(self) -> None:
        json_dup = '{"projeto": "A", "projeto": "B", "classe_risco": "risco_leve"}'
        with self.assertRaises(ValueError):
            decodificar_instalacao_json(json_dup)

    def test_rejeicao_float_nativo_no_json(self) -> None:
        json_float = '{"projeto": "A", "area_compartimento_m2": 500.5}'
        with self.assertRaises(TypeError):
            decodificar_instalacao_json(json_float)

    def test_rejeicao_profundidade_excessiva(self) -> None:
        profundo: dict = {"nivel": 0}
        atual = profundo
        for i in range(1, 35):
            atual["prox"] = {"nivel": i}
            atual = atual["prox"]

        texto_profundo = json.dumps(profundo)
        with self.assertRaises(ValueError):
            decodificar_instalacao_json(texto_profundo)

    def test_serializacao_e_roundtrip(self) -> None:
        ex_path = Path(__file__).resolve().parent.parent / "examples" / "edificio_escritorios_risco_leve.json"
        inst = decodificar_instalacao_json(ex_path.read_text(encoding="utf-8"))
        res = calcular_sprinklers_nbr10897(inst)

        dict_inst = instalacao_para_dict(inst)
        self.assertEqual(dict_inst["classe_risco"], "risco_leve")

        dict_res = resultado_para_dict(res)
        self.assertEqual(dict_res["fator_k"], 80)

        json_str = codificar_resultado_json(res)
        self.assertIn('"fator_k": 80', json_str)
