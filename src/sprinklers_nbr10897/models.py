"""Modelos de dados imutáveis para dimensionamento de sprinklers NBR 10897:2020.

Garante imutabilidade (frozen=True) e tipagem estrita com Fraction e inteiros.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class BicoSprinkler:
    """Configuração do chuveiro automático (sprinkler) adotado."""

    modelo_fator_k: str
    espacamento_s_m: Fraction
    espacamento_l_m: Fraction

    def __post_init__(self) -> None:
        if self.espacamento_s_m <= 0 or self.espacamento_l_m <= 0:
            raise ValueError("Os espaçamentos entre bicos devem ser estritamente positivos.")

    @property
    def area_cobertura_m2(self) -> Fraction:
        """Área de cobertura atendida por cada bico (S * L)."""
        return self.espacamento_s_m * self.espacamento_l_m


@dataclass(frozen=True)
class ConexoesTrecho:
    """Contagem de conexões hidráulicas presentes em um trecho."""

    joelho_90: int = 0
    te_passagem_direta: int = 0
    te_saida_lateral: int = 0
    valvula_gaveta: int = 0
    valvula_retencao: int = 0

    def __post_init__(self) -> None:
        for campo, val in (
            ("joelho_90", self.joelho_90),
            ("te_passagem_direta", self.te_passagem_direta),
            ("te_saida_lateral", self.te_saida_lateral),
            ("valvula_gaveta", self.valvula_gaveta),
            ("valvula_retencao", self.valvula_retencao),
        ):
            if val < 0:
                raise ValueError(f"Quantidade de conexões '{campo}' não pode ser negativa.")


@dataclass(frozen=True)
class TrechoRede:
    """Trecho de tubulação da rede de sprinklers."""

    identificador: str
    tubo_id: str
    comprimento_real_m: Fraction
    desnivel_geometrico_m: Fraction
    conexoes: ConexoesTrecho
    tem_vga: bool = False

    def __post_init__(self) -> None:
        if not self.identificador.strip():
            raise ValueError("O identificador do trecho não pode ser vazio.")
        if self.comprimento_real_m < 0:
            raise ValueError("O comprimento real do trecho não pode ser negativo.")


@dataclass(frozen=True)
class InstalacaoSprinklers:
    """Definição completa da instalação de chuveiros automáticos."""

    projeto: str
    classe_risco: str
    area_compartimento_m2: Fraction
    bico: BicoSprinkler
    trechos: tuple[TrechoRede, ...]
    margem_desbalanceamento_pct: Fraction = Fraction(15, 1)
    rendimento_bomba: Fraction = Fraction(65, 100)

    def __post_init__(self) -> None:
        if not self.projeto.strip():
            raise ValueError("O nome do projeto não pode ser vazio.")
        if self.area_compartimento_m2 <= 0:
            raise ValueError("A área do compartimento deve ser estritamente positiva.")
        if len(self.trechos) == 0:
            raise ValueError("A instalação deve conter pelo menos um trecho de tubulação.")
        if self.margem_desbalanceamento_pct < 0:
            raise ValueError("A margem de desbalanceamento hidráulico não pode ser negativa.")
        if self.rendimento_bomba <= 0 or self.rendimento_bomba > 1:
            raise ValueError("O rendimento da bomba deve estar no intervalo (0, 1].")


@dataclass(frozen=True)
class ResultadoTrecho:
    """Resultado hidráulico individual de um trecho da rede de tubulações."""

    identificador: str
    tubo_id: str
    dn_pol: str
    diametro_interno_mm: Fraction
    vazao_l_min: Fraction
    velocidade_m_s: Fraction
    comprimento_real_m: Fraction
    comprimento_equivalente_m: Fraction
    comprimento_total_m: Fraction
    perda_unitaria_mca_m: Fraction
    perda_carga_mca: Fraction
    desnivel_m: Fraction


@dataclass(frozen=True)
class ResultadoDimensionamentoSprinklers:
    """Resultado executivo consolidado do dimensionamento NBR 10897:2020."""

    projeto: str
    classe_risco: str
    nome_classe_risco: str
    densidade_adotada_mm_min: Fraction
    area_operacao_adotada_m2: Fraction
    area_por_bico_m2: Fraction
    vazao_bico_critico_l_min: Fraction
    pressao_minima_bico_mca: Fraction
    fator_k: int
    numero_bicos_operacao: int
    vazao_bicos_l_min: Fraction
    vazao_sprinklers_desbalanceada_l_min: Fraction
    vazao_hidrantes_adicionais_l_min: Fraction
    vazao_total_sistema_l_min: Fraction
    tempo_minimo_rti_min: int
    volume_rti_m3: Fraction
    trechos: tuple[ResultadoTrecho, ...]
    perda_carga_total_tubulacao_mca: Fraction
    desnivel_geometrico_total_m: Fraction
    altura_manometrica_total_mca: Fraction
    potencia_bomba_cv: Fraction
    potencia_comercial_bomba_cv: int
    atende_norma: bool
    observacoes: tuple[str, ...]
