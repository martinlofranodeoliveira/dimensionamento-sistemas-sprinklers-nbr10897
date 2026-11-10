"""Testes unitários para empacotamento e integridade de arquivos do projeto."""

from __future__ import annotations

from pathlib import Path
import tomllib


def test_arquivos_raiz_obrigatorios() -> None:
    raiz = Path(__file__).resolve().parent.parent
    obrigatorios = [
        "pyproject.toml",
        "LICENSE",
        "README.md",
        ".gitignore",
        "src/sprinklers_nbr10897/__init__.py",
        "src/sprinklers_nbr10897/py.typed",
        "tools/verify_independent.py",
        "scripts/check_distribution.py",
        "scripts/generate_assets.py",
    ]
    for ob in obrigatorios:
        p = raiz / ob
        assert p.exists(), f"Arquivo obrigatório '{ob}' não encontrado."


def test_pyproject_toml_metadados() -> None:
    raiz = Path(__file__).resolve().parent.parent
    conteudo = (raiz / "pyproject.toml").read_text(encoding="utf-8")
    dados = tomllib.loads(conteudo)

    proj = dados["project"]
    assert proj["name"] == "dimensionamento-sistemas-sprinklers-nbr10897"
    assert proj["version"] == "1.0.0"
    assert "Lofrano" in proj["authors"][0]["name"]
    assert "sprinklers-nbr10897" in proj["scripts"]


def test_versao_init() -> None:
    from sprinklers_nbr10897 import __version__
    assert __version__ == "1.0.0"


def test_exports_completos() -> None:
    import sprinklers_nbr10897 as spk
    assert hasattr(spk, "calcular_sprinklers_nbr10897")
    assert hasattr(spk, "InstalacaoSprinklers")
    assert hasattr(spk, "gerar_painel_svg")
    assert hasattr(spk, "gerar_relatorio_texto")

