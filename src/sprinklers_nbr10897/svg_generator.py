"""Gerador de painel executivo vetorial SVG (1440x900) para NBR 10897:2020.

Cria diagrama esquemático e painel de indicadores com estética de alta precisão
técnica para sistemas de proteção contra incêndio por chuveiros automáticos.
"""

from __future__ import annotations

import html
from sprinklers_nbr10897.exporters import formatar_fracao_decimal
from sprinklers_nbr10897.models import ResultadoDimensionamentoSprinklers


def gerar_painel_svg(res: ResultadoDimensionamentoSprinklers) -> str:
    """Gera visualização técnica SVG 1440x900 do dimensionamento de sprinklers."""
    projeto_esc = html.escape(res.projeto)
    classe_esc = html.escape(res.nome_classe_risco)
    status_cor = "#10b981" if res.atende_norma else "#f59e0b"
    status_texto = "CONFORME NBR 10897:2020" if res.atende_norma else "REQUER ATENÇÃO / NÃO CONFORME"

    svg_linhas = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" width="1440" height="900">',
        '  <defs>',
        '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#0b1120"/>',
        '      <stop offset="100%" stop-color="#0f172a"/>',
        '    </linearGradient>',
        '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#1e293b"/>',
        '      <stop offset="100%" stop-color="#162032"/>',
        '    </linearGradient>',
        '    <linearGradient id="redAccent" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#ef4444"/>',
        '      <stop offset="100%" stop-color="#f97316"/>',
        '    </linearGradient>',
        '    <linearGradient id="blueAccent" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#06b6d4"/>',
        '      <stop offset="100%" stop-color="#3b82f6"/>',
        '    </linearGradient>',
        '    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">',
        '      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>',
        '    </filter>',
        '  </defs>',
        '  <!-- Plano de Fundo -->',
        '  <rect width="1440" height="900" fill="url(#bgGrad)"/>',
        '',
        '  <!-- Cabeçalho -->',
        '  <rect x="40" y="30" width="1360" height="90" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '  <rect x="40" y="30" width="6" height="90" rx="3" fill="url(#redAccent)"/>',
        '  <text x="65" y="65" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="700">LOFRANO TECNOLOGIA | DIMENSIONAMENTO DE SISTEMAS DE SPRINKLERS</text>',
        '  <text x="65" y="95" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="14">ABNT NBR 10897:2020 • Projeto: <tspan fill="#38bdf8" font-weight="600">' + projeto_esc + '</tspan> • Ocupação: <tspan fill="#cbd5e1">' + classe_esc + '</tspan></text>',
        '  <rect x="1140" y="55" width="230" height="40" rx="20" fill="' + status_cor + '" fill-opacity="0.15" stroke="' + status_cor + '" stroke-width="1.5"/>',
        '  <circle cx="1160" cy="75" r="6" fill="' + status_cor + '"/>',
        '  <text x="1178" y="80" fill="' + status_cor + '" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="700">' + status_texto + '</text>',
        '',
        '  <!-- Indicadores KPI -->',
        '  <!-- KPI 1: Vazão Total -->',
        '  <g transform="translate(40, 140)">',
        '    <rect width="255" height="100" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '    <text x="20" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">VAZÃO TOTAL DO SISTEMA</text>',
        f'    <text x="20" y="70" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{formatar_fracao_decimal(res.vazao_total_sistema_l_min, 1)}</text>',
        '    <text x="180" y="68" fill="#64748b" font-family="system-ui, sans-serif" font-size="14">L/min</text>',
        f'    <text x="20" y="88" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Sprinklers: {formatar_fracao_decimal(res.vazao_sprinklers_desbalanceada_l_min, 1)} L/min</text>',
        '  </g>',
        '',
        '  <!-- KPI 2: Bicos em Operação -->',
        '  <g transform="translate(315, 140)">',
        '    <rect width="255" height="100" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '    <text x="20" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">BICOS EM OPERAÇÃO</text>',
        f'    <text x="20" y="70" fill="#f97316" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{res.numero_bicos_operacao}</text>',
        f'    <text x="80" y="68" fill="#64748b" font-family="system-ui, sans-serif" font-size="14">chuveiros (K{res.fator_k})</text>',
        f'    <text x="20" y="88" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Área Cálculo: {formatar_fracao_decimal(res.area_operacao_adotada_m2, 0)} m²</text>',
        '  </g>',
        '',
        '  <!-- KPI 3: Reserva Técnica (RTI) -->',
        '  <g transform="translate(590, 140)">',
        '    <rect width="255" height="100" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '    <text x="20" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">RESERVA TÉCNICA (RTI)</text>',
        f'    <text x="20" y="70" fill="#10b981" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{formatar_fracao_decimal(res.volume_rti_m3, 1)}</text>',
        '    <text x="140" y="68" fill="#64748b" font-family="system-ui, sans-serif" font-size="14">m³</text>',
        f'    <text x="20" y="88" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Autonomia: {res.tempo_minimo_rti_min} min</text>',
        '  </g>',
        '',
        '  <!-- KPI 4: Altura Manométrica -->',
        '  <g transform="translate(865, 140)">',
        '    <rect width="255" height="100" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '    <text x="20" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">ALTURA MANOMÉTRICA (Hman)</text>',
        f'    <text x="20" y="70" fill="#a855f7" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{formatar_fracao_decimal(res.altura_manometrica_total_mca, 1)}</text>',
        '    <text x="160" y="68" fill="#64748b" font-family="system-ui, sans-serif" font-size="14">mca</text>',
        f'    <text x="20" y="88" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Bico Crítico: {formatar_fracao_decimal(res.pressao_minima_bico_mca, 1)} mca</text>',
        '  </g>',
        '',
        '  <!-- KPI 5: Moto-Bomba -->',
        '  <g transform="translate(1140, 140)">',
        '    <rect width="260" height="100" rx="10" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '    <text x="20" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">MOTO-BOMBA PRINCIPAL</text>',
        f'    <text x="20" y="70" fill="#ef4444" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{res.potencia_comercial_bomba_cv}</text>',
        '    <text x="75" y="68" fill="#64748b" font-family="system-ui, sans-serif" font-size="14">cv comercial</text>',
        f'    <text x="20" y="88" fill="#64748b" font-family="system-ui, sans-serif" font-size="11">Cálculo: {formatar_fracao_decimal(res.potencia_bomba_cv, 2)} cv (η=65%)</text>',
        '  </g>',
        '',
        '  <!-- Painel Esquerdo: Esquema Hidráulico da Instalação -->',
        '  <g transform="translate(40, 260)">',
        '    <rect width="780" height="570" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '    <text x="25" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="700">DIAGRAMA HIDRÁULICO DO SISTEMA (NBR 10897 / NBR 5580)</text>',
        '    <text x="25" y="58" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">Reservatório RTI ➔ Conjunto Moto-Bomba ➔ VGA ➔ Coluna Principal ➔ Ramais de Sprinklers</text>',
        '',
        '    <!-- Reservatório de Incêndio -->',
        '    <g transform="translate(40, 340)">',
        '      <rect width="130" height="160" rx="8" fill="#0f172a" stroke="#0284c7" stroke-width="2"/>',
        '      <rect x="5" y="40" width="120" height="115" rx="4" fill="#0284c7" fill-opacity="0.3"/>',
        f'      <text x="65" y="25" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">RESERVATÓRIO</text>',
        f'      <text x="65" y="90" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="800" text-anchor="middle">RTI</text>',
        f'      <text x="65" y="115" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700" text-anchor="middle">{formatar_fracao_decimal(res.volume_rti_m3, 1)} m³</text>',
        '    </g>',
        '',
        '    <!-- Tubulação de Sucção -->',
        '    <path d="M 170 460 L 220 460" stroke="#38bdf8" stroke-width="6" fill="none"/>',
        '',
        '    <!-- Moto-Bomba de Incêndio -->',
        '    <g transform="translate(220, 410)">',
        '      <circle cx="45" cy="50" r="35" fill="#1e293b" stroke="#ef4444" stroke-width="3"/>',
        '      <polygon points="40,30 65,50 40,70" fill="#ef4444"/>',
        '      <rect x="15" y="88" width="60" height="8" rx="2" fill="#64748b"/>',
        f'      <text x="45" y="115" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="11" font-weight="700" text-anchor="middle">BOMBA {res.potencia_comercial_bomba_cv} CV</text>',
        f'      <text x="45" y="130" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="10" text-anchor="middle">Hman: {formatar_fracao_decimal(res.altura_manometrica_total_mca, 1)} mca</text>',
        '    </g>',
        '',
        '    <!-- Recalque / VGA -->',
        '    <path d="M 300 460 L 350 460 L 350 360" stroke="#ef4444" stroke-width="6" fill="none"/>',
        '    <!-- Bloco VGA -->',
        '    <g transform="translate(325, 290)">',
        '      <rect width="50" height="65" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>',
        '      <text x="25" y="28" fill="#f59e0b" font-family="system-ui, sans-serif" font-size="10" font-weight="700" text-anchor="middle">VGA</text>',
        '      <text x="25" y="45" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="9" text-anchor="middle">Gongo</text>',
        '      <circle cx="25" cy="55" r="3" fill="#f59e0b"/>',
        '    </g>',
        '',
        '    <!-- Coluna Principal (Riser) -->',
        '    <path d="M 350 290 L 350 130 L 450 130" stroke="#f97316" stroke-width="6" fill="none"/>',
        '    <text x="360" y="210" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">Coluna Montante (Riser)</text>',
        '',
        '    <!-- Ramais e Bicos de Sprinklers -->',
        '    <g transform="translate(450, 80)">',
        '      <!-- Tubo Distribuidor Principal -->',
        '      <line x1="0" y1="50" x2="280" y2="50" stroke="#f97316" stroke-width="5"/>',
        '      <!-- Ramal Superior -->',
        '      <line x1="60" y1="50" x2="60" y2="20" stroke="#38bdf8" stroke-width="3"/>',
        '      <line x1="20" y1="20" x2="100" y2="20" stroke="#38bdf8" stroke-width="3"/>',
        '      <!-- Bicos Ramal 1 -->',
        '      <circle cx="30" cy="20" r="4" fill="#ef4444"/>',
        '      <circle cx="90" cy="20" r="4" fill="#ef4444"/>',
        '      <!-- Borrifo água 1 -->',
        '      <path d="M 30 15 L 20 0 M 30 15 L 30 -2 M 30 15 L 40 0" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>',
        '      <path d="M 90 15 L 80 0 M 90 15 L 90 -2 M 90 15 L 100 0" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>',
        '',
        '      <!-- Ramal Central -->',
        '      <line x1="160" y1="50" x2="160" y2="120" stroke="#38bdf8" stroke-width="3"/>',
        '      <line x1="120" y1="120" x2="200" y2="120" stroke="#38bdf8" stroke-width="3"/>',
        '      <!-- Bicos Ramal 2 -->',
        '      <circle cx="130" cy="120" r="4" fill="#ef4444"/>',
        '      <circle cx="190" cy="120" r="4" fill="#ef4444"/>',
        '      <!-- Borrifo água 2 -->',
        '      <path d="M 130 125 L 120 140 M 130 125 L 130 143 M 130 125 L 140 140" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>',
        '      <path d="M 190 125 L 180 140 M 190 125 L 190 143 M 190 125 L 200 140" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>',
        '',
        '      <!-- Ramal Crítico (Mais Desfavorável) -->',
        '      <line x1="250" y1="50" x2="250" y2="200" stroke="#ef4444" stroke-width="3" stroke-dasharray="4,2"/>',
        '      <line x1="200" y1="200" x2="270" y2="200" stroke="#ef4444" stroke-width="3"/>',
        '      <circle cx="260" cy="200" r="6" fill="#ef4444" stroke="#f8fafc" stroke-width="2"/>',
        f'      <text x="260" y="235" fill="#fca5a5" font-family="system-ui, sans-serif" font-size="11" font-weight="700" text-anchor="middle">BICO CRÍTICO</text>',
        f'      <text x="260" y="250" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="10" text-anchor="middle">P = {formatar_fracao_decimal(res.pressao_minima_bico_mca, 1)} mca</text>',
        f'      <text x="260" y="265" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="10" text-anchor="middle">q = {formatar_fracao_decimal(res.vazao_bico_critico_l_min, 1)} L/min</text>',
        '    </g>',
        '  </g>',
        '',
        '  <!-- Painel Direito: Tabela de Trechos e Parecer Técnico -->',
        '  <g transform="translate(840, 260)">',
        '    <rect width="560" height="570" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" filter="url(#cardShadow)"/>',
        '    <text x="25" y="35" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="16" font-weight="700">TRECHOS HIDRÁULICOS (NBR 5580)</text>',
        '    <text x="25" y="58" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12">Perdas de carga contínuas, conexões e velocidades</text>',
        '',
        '    <!-- Cabeçalho Tabela -->',
        '    <rect x="25" y="80" width="510" height="30" rx="4" fill="#0f172a"/>',
        '    <text x="35" y="100" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" font-weight="700">TRECHO</text>',
        '    <text x="180" y="100" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" font-weight="700">DN</text>',
        '    <text x="260" y="100" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" font-weight="700">L.TOT(m)</text>',
        '    <text x="350" y="100" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" font-weight="700">ΔH(mca)</text>',
        '    <text x="445" y="100" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11" font-weight="700">v(m/s)</text>',
    ]

    y_tabela = 130
    for idx, t in enumerate(res.trechos[:6]):
        cor_linha = "#162032" if idx % 2 == 0 else "#1e293b"
        nome_curto = t.identificador if len(t.identificador) <= 18 else t.identificador[:16] + ".."
        svg_linhas.extend([
            f'    <rect x="25" y="{y_tabela - 16}" width="510" height="26" rx="2" fill="{cor_linha}"/>',
            f'    <text x="35" y="{y_tabela}" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="11">{html.escape(nome_curto)}</text>',
            f'    <text x="180" y="{y_tabela}" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="11">{t.dn_pol}</text>',
            f'    <text x="260" y="{y_tabela}" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">{formatar_fracao_decimal(t.comprimento_total_m, 1)}</text>',
            f'    <text x="350" y="{y_tabela}" fill="#fca5a5" font-family="system-ui, sans-serif" font-size="11">{formatar_fracao_decimal(t.perda_carga_mca, 2)}</text>',
            f'    <text x="445" y="{y_tabela}" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="11">{formatar_fracao_decimal(t.velocidade_m_s, 2)}</text>',
        ])
        y_tabela += 28

    # Caixa de Observações e Parecer
    svg_linhas.extend([
        '',
        '    <!-- Caixa de Parecer Normativo -->',
        '    <g transform="translate(25, 340)">',
        '      <rect width="510" height="200" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>',
        '      <text x="20" y="30" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700">PARECER TÉCNICO NORMATIVO</text>',
    ])

    y_obs = 60
    for obs in res.observacoes[:4]:
        obs_esc = html.escape(obs)
        if len(obs_esc) > 75:
            obs_esc = obs_esc[:72] + "..."
        svg_linhas.append(
            f'      <text x="20" y="{y_obs}" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">• {obs_esc}</text>'
        )
        y_obs += 26

    svg_linhas.extend([
        f'      <line x1="20" y1="160" x2="490" y2="160" stroke="#1e293b" stroke-width="1"/>',
        f'      <text x="20" y="182" fill="#64748b" font-family="system-ui, sans-serif" font-size="10">Dimensionamento estritamente conforme ABNT NBR 10897:2020 e NBR 5580.</text>',
        '    </g>',
        '  </g>',
        '',
        '  <!-- Rodapé -->',
        '  <text x="720" y="870" fill="#64748b" font-family="system-ui, sans-serif" font-size="12" text-anchor="middle">Engenharia de Incêndio • Lofrano Tecnologia 2026 • 100% Aritmética Racional Exata (Zero Float)</text>',
        '</svg>',
    ])

    return "\n".join(svg_linhas)
