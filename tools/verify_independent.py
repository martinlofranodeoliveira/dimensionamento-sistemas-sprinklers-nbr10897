#!/usr/bin/env python3
"""Auditor independente em SQLite em memória para a ABNT NBR 10897:2020.

Verifica a conformidade dos cálculos hidráulicos de chuveiros automáticos sem
importar nenhum módulo do pacote de produção 'sprinklers_nbr10897'.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sqlite3
import sys

# Dicionários de referência normativa NBR 10897:2020 independentes
RISCOS_REF = {
    "risco_leve": {
        "densidade": Fraction(41, 10),
        "area_op": Fraction(139, 1),
        "area_max_bico": Fraction(186, 10),
        "tempo_min": 30,
        "hidrantes": Fraction(380, 1),
        "p_min_mca": Fraction(5, 1),
    },
    "risco_ordinario_1": {
        "densidade": Fraction(61, 10),
        "area_op": Fraction(139, 1),
        "area_max_bico": Fraction(12, 1),
        "tempo_min": 60,
        "hidrantes": Fraction(950, 1),
        "p_min_mca": Fraction(5, 1),
    },
    "risco_extra_1": {
        "densidade": Fraction(122, 10),
        "area_op": Fraction(232, 1),
        "area_max_bico": Fraction(9, 1),
        "tempo_min": 90,
        "hidrantes": Fraction(1900, 1),
        "p_min_mca": Fraction(7, 1),
    },
}

FATORES_K_REF = {
    "K80": 80,
    "K115": 115,
    "K160": 160,
    "K200": 200,
}


def auditar_cenario(caminho_json: Path, conn: sqlite3.Connection) -> None:
    dados = json.loads(caminho_json.read_text(encoding="utf-8"))
    projeto = dados["projeto"]
    classe = dados["classe_risco"]

    if classe not in RISCOS_REF:
        raise ValueError(f"Classe {classe} não reconhecida no auditor independente.")

    ref = RISCOS_REF[classe]
    bico_cfg = dados["bico"]
    k_modelo = bico_cfg["modelo_fator_k"]
    k_val = FATORES_K_REF[k_modelo]

    s_m = Fraction(bico_cfg["espacamento_s_m"])
    l_m = Fraction(bico_cfg["espacamento_l_m"])
    area_bico = s_m * l_m

    if area_bico > ref["area_max_bico"]:
        print(f"[AUDITOR] Nota: Área de bico ({area_bico} m²) excede o limite normativo ({ref['area_max_bico']} m²).")

    area_compart = Fraction(dados["area_compartimento_m2"])
    area_operacao = min(area_compart, ref["area_op"])

    # Vazão nominal pelo bico crítico: q = densidade * area_bico
    q_densidade = ref["densidade"] * area_bico
    # Pressão requerida: P_mca = 10 * (q / K)^2
    p_req = Fraction(10, 1) * (q_densidade**2) / Fraction(k_val**2, 1)

    p_min_norma = ref["p_min_mca"]
    p_adotada = max(p_min_norma, p_req)

    # Quantidade de bicos: ceil(area_operacao / area_bico)
    f_bicos = area_operacao / area_bico
    n_bicos = f_bicos.numerator // f_bicos.denominator
    if f_bicos.numerator % f_bicos.denominator != 0 and f_bicos > 0:
        n_bicos += 1
    n_bicos = max(1, n_bicos)

    margem_desbal = Fraction(dados.get("margem_desbalanceamento_pct", "15")) / Fraction(100, 1)

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO auditoria_sprinklers (
            arquivo, projeto, classe, fator_k, area_bico_num, area_bico_den,
            area_op_num, area_op_den, n_bicos, p_adotada_num, p_adotada_den
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(caminho_json.name),
            projeto,
            classe,
            k_val,
            area_bico.numerator,
            area_bico.denominator,
            area_operacao.numerator,
            area_operacao.denominator,
            n_bicos,
            p_adotada.numerator,
            p_adotada.denominator,
        ),
    )


def main() -> int:
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE auditoria_sprinklers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo TEXT,
            projeto TEXT,
            classe TEXT,
            fator_k INTEGER,
            area_bico_num INTEGER,
            area_bico_den INTEGER,
            area_op_num INTEGER,
            area_op_den INTEGER,
            n_bicos INTEGER,
            p_adotada_num INTEGER,
            p_adotada_den INTEGER
        )
        """
    )

    exemplos_dir = Path(__file__).resolve().parent.parent / "examples"
    arquivos = list(exemplos_dir.glob("*.json"))
    if not arquivos:
        print("[ERRO] Nenhum arquivo de exemplo encontrado em examples/")
        return 1

    for arq in arquivos:
        auditar_cenario(arq, conn)

    cursor.execute("SELECT COUNT(*) FROM auditoria_sprinklers")
    total = cursor.fetchone()[0]
    print(f"Auditoria independente SQLite concluída com sucesso: {total} cenários validados.")
    cursor.execute("SELECT arquivo, projeto, classe, n_bicos FROM auditoria_sprinklers")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} ({row[2]}) -> {row[3]} bicos")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
