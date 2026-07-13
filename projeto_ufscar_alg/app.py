"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          SIMULADOR DE LINHA DE PRODUÇÃO — DASHBOARD INTERATIVO               ║
║          Disciplina: Algoritmos e Programação Computacional                  ║
║          Prof. Dr. José A. Salim                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Dependências:
    pip install streamlit plotly pandas numpy

Execução:
    streamlit run app.py

Este arquivo agora só orquestra a interface. A lógica de negócio,
os estilos, o tema dos gráficos e o gerenciamento de estado vivem em
módulos separados: logic.py, styles.py, viz_theme.py e state.py.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random

from styles import apply_styles
from viz_theme import LAYOUT, LEGEND, GRID, C, PAL, ax
from state import (
    init_state,
    adicionar_maquina,
    remover_maquina,
    aplicar_preset,
    preset_widget_key,
    bump_preset_reset,
    PRESETS,
    PRESET_LABELS,
    PRESET_PLACEHOLDER,
)
from logic import (
    criar_maquina,
    calcular_prob_serie,
    calcular_prob_paralelo,
    calcular_tempo_ciclo,
    calcular_mttf,
    identificar_gargalos,
    analisar_impacto_falha,
    simular_monte_carlo,
    calcular_producao_esperada,
)

st.set_page_config(
    page_title="SimProd · Linha de Produção",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_styles()
init_state()


# ─────────────────────────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='masthead'>
    <div class='masthead-left'>
        <div class='masthead-logo'>SIM<span>PROD</span></div>
        <div class='masthead-rule'></div>
        <div class='masthead-sub'>
            Simulador de Linha de Produção<br>
            <strong>Confiabilidade &amp; Monte Carlo</strong>
        </div>
    </div>
    <div class='masthead-tag'>
        ALGORITMOS E PROG. COMPUTACIONAL<br>
        PROF. DR. JOSÉ A. SALIM
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ETAPA 1 — CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='sec-label'>
    <span class='sec-num'>01</span>
    <span class='sec-title'>CONFIGURAÇÃO GERAL</span>
    <span class='sec-line'></span>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='config-strip'>", unsafe_allow_html=True)
    cfg1, cfg2, cfg3, cfg4 = st.columns([1.4, 1, 1, 1.3])
    with cfg1:
        config = st.selectbox(
            "Topologia da linha",
            options=['serie', 'paralelo'],
            format_func=lambda x: "Série — sequencial" if x == 'serie' else "Paralelo — simultâneo",
        )
    with cfg2:
        horas_dia = st.number_input("Horas / dia", 1, 24, 8)
    with cfg3:
        dias_mes = st.number_input("Dias / mês", 1, 31, 20)
    with cfg4:
        iteracoes_mc = st.select_slider(
            "Iterações Monte Carlo",
            options=[500, 1000, 2000, 5000, 10000],
            value=5000,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ETAPA 2 — MÁQUINAS (cartões clicáveis, sem tabela para digitar)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='sec-label'>
    <span class='sec-num'>02</span>
    <span class='sec-title'>MÁQUINAS DA LINHA</span>
    <span class='sec-line'></span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='picker-hint'>
    Cada máquina é um cartão independente. Abra, ajuste com os controles deslizantes
    ou escolha um perfil pronto — não é preciso digitar em nenhuma tabela.
</div>
""", unsafe_allow_html=True)

# Barra de ações: adicionar máquina (com preset) + limpar tudo
add_col1, add_col2, add_col3 = st.columns([2, 2, 1])
with add_col1:
    preset_para_nova = st.selectbox(
        "Perfil da nova máquina",
        options=PRESET_LABELS,
        key="preset_nova_maquina",
        label_visibility="collapsed",
    )
with add_col2:
    if st.button("➕ ADICIONAR MÁQUINA", use_container_width=True):
        adicionar_maquina(preset_para_nova)
        st.rerun()
with add_col3:
    if st.button("🗑 LIMPAR TUDO", use_container_width=True, type="secondary"):
        st.session_state.maquinas_lista = []
        st.rerun()

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# Cartões editáveis — um expander por máquina, com sliders/toggle/selects.
for m in st.session_state.maquinas_lista:
    status_icon = "🟢" if m["ativa"] else "⚪"
    header = f"{status_icon}  {m['nome']}  ·  {m['tempo_operacao']:.1f} min  ·  {m['prob_falha']*100:.0f}% falha"
    with st.expander(header, expanded=False):
        row1_a, row1_b, row1_c = st.columns([2, 1, 1])
        with row1_a:
            novo_nome = st.text_input("Nome da máquina", value=m["nome"], key=f"nome_{m['id']}")
            m["nome"] = novo_nome or m["nome"]
        with row1_b:
            m["ativa"] = st.toggle("Ativa na linha", value=m["ativa"], key=f"ativa_{m['id']}")
        with row1_c:
            # FIX: versões recentes do Streamlit não permitem mais escrever em
            # st.session_state[key] de um widget já instanciado no mesmo run
            # (mesmo antes de um st.rerun()) — isso agora lança
            # StreamlitAPIException. Em vez de tentar resetar o selectbox
            # sobrescrevendo sua própria key, trocamos a key do widget
            # (via preset_widget_key, que embute um contador por máquina).
            # Assim, no próximo run, nasce um widget NOVO já no placeholder,
            # sem mexer no estado do widget antigo.
            preset_key = preset_widget_key(m["id"])
            preset_escolhido = st.selectbox(
                "Aplicar perfil pronto",
                options=[PRESET_PLACEHOLDER] + PRESET_LABELS,
                key=preset_key,
            )
            if preset_escolhido != PRESET_PLACEHOLDER:
                aplicar_preset(m["id"], preset_escolhido)
                bump_preset_reset(m["id"])
                st.rerun()

        row2_a, row2_b, row2_c = st.columns(3)
        with row2_a:
            m["tempo_operacao"] = st.slider(
                "Tempo de operação (min)", 0.5, 120.0, float(m["tempo_operacao"]), 0.5,
                key=f"top_{m['id']}",
            )
        with row2_b:
            m["prob_falha"] = st.slider(
                "Probabilidade de falha", 0.0, 1.0, float(m["prob_falha"]), 0.01,
                key=f"pf_{m['id']}",
                help="Chance de a máquina falhar em cada ciclo de operação.",
            )
        with row2_c:
            m["tempo_manutencao"] = st.slider(
                "Tempo de manutenção (min)", 0.0, 180.0, float(m["tempo_manutencao"]), 1.0,
                key=f"tman_{m['id']}",
            )

        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
        if st.button("Remover esta máquina", key=f"rm_{m['id']}", type="secondary", use_container_width=True):
            remover_maquina(m["id"])
            st.rerun()

maquinas = [
    criar_maquina(
        m["nome"],
        float(m["tempo_operacao"]),
        float(min(max(m["prob_falha"], 0.0), 1.0)),
        float(m["tempo_manutencao"]),
    )
    for m in st.session_state.maquinas_lista if m["ativa"] and m["tempo_operacao"] > 0
]
nomes = [m['nome'] for m in maquinas]

_, run_col = st.columns([3, 1])
with run_col:
    if st.button("▶ EXECUTAR SIMULAÇÃO", use_container_width=True):
        with st.spinner("Rodando simulação Monte Carlo..."):
            import time as _time
            _time.sleep(0.4)  # feedback perceptível; os cálculos abaixo já são instantâneos
        st.toast("Simulação atualizada com os parâmetros atuais.", icon="✅")

# Mini cards por máquina (resumo visual, somente leitura)
if maquinas:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    mcols = st.columns(min(len(maquinas), 5))
    accent_colors = [C['blue'], C['white'], C['amber'], C['red'], C['green']]
    for i, m in enumerate(maquinas):
        cor = accent_colors[i % len(accent_colors)]
        disp_pct = m['disponibilidade'] * 100
        mtbf_str = f"{m['tempo_mtbf']/60:.1f} h" if m['tempo_mtbf'] != float('inf') else "∞"
        with mcols[i % len(mcols)]:
            st.markdown(f"""
            <div class='mcard'>
                <div class='mcard-header'>
                    <div class='mcard-accent' style='background:{cor}'></div>
                    <div class='mcard-name'>{m['nome']}</div>
                </div>
                <div class='mcard-row'><span>OPERAÇÃO</span><b>{m['tempo_operacao']:.1f} MIN</b></div>
                <div class='mcard-row'><span>P. FALHA</span><b>{m['prob_falha']*100:.1f}%</b></div>
                <div class='mcard-row'><span>DISPONIB.</span><b>{disp_pct:.1f}%</b></div>
                <div class='mcard-row'><span>MTBF</span><b>{mtbf_str}</b></div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class='empty-state'>
        <div class='empty-title'>NENHUMA MÁQUINA ATIVA</div>
        <div>Clique em "➕ ADICIONAR MÁQUINA" acima e deixe o cartão marcado como "Ativa" para iniciar.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULOS
# ─────────────────────────────────────────────────────────────────────────────

if config == 'serie':
    prob_falha, prob_func = calcular_prob_serie(maquinas)
else:
    prob_falha, prob_func = calcular_prob_paralelo(maquinas)

tc = calcular_tempo_ciclo(maquinas, config)
mttf = calcular_mttf(maquinas, config)
prod = calcular_producao_esperada(maquinas, config, horas_dia, dias_mes)
mc = simular_monte_carlo(maquinas, config, iteracoes_mc)
g_lenta, g_critica, g_indisp = identificar_gargalos(maquinas)
impactos = analisar_impacto_falha(maquinas, config)


# ─────────────────────────────────────────────────────────────────────────────
# ETAPA 3 — RESULTADOS
# ─────────────────────────────────────────────────────────────────────────────

conf_label = "SÉRIE" if config == "serie" else "PARALELO"
st.markdown(f"""
<div class='sec-label'>
    <span class='sec-num'>03</span>
    <span class='sec-title'>RESULTADOS — {conf_label} · {len(maquinas)} MÁQ. · {iteracoes_mc:,} ITER.</span>
    <span class='sec-line'></span>
</div>
""", unsafe_allow_html=True)


# KPI ROW 1
k1, k2, k3, k4 = st.columns(4)

with k1:
    cor = "blue" if prob_func >= 0.8 else ("amber" if prob_func >= 0.5 else "red")
    lbl = "ALTA" if prob_func >= 0.8 else ("MÉDIA" if prob_func >= 0.5 else "BAIXA")
    st.markdown(f"""
    <div class='kpi kpi-{cor}'>
        <div class='kpi-eyebrow'>Confiabilidade</div>
        <div class='kpi-value'>{prob_func*100:.1f}<small>%</small></div>
        <div class='kpi-sub'>P(sistema funciona)</div>
        <span class='kpi-badge badge-{cor}'>{lbl}</span>
    </div>
    """, unsafe_allow_html=True)

with k2:
    cor2 = "red" if prob_falha >= 0.3 else ("amber" if prob_falha >= 0.1 else "green")
    lbl2 = "CRÍTICO" if prob_falha >= 0.3 else ("ATENÇÃO" if prob_falha >= 0.1 else "NORMAL")
    st.markdown(f"""
    <div class='kpi kpi-{cor2}'>
        <div class='kpi-eyebrow'>Risco de Falha</div>
        <div class='kpi-value'>{prob_falha*100:.1f}<small>%</small></div>
        <div class='kpi-sub'>P(sistema falha)</div>
        <span class='kpi-badge badge-{cor2}'>{lbl2}</span>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class='kpi kpi-blue'>
        <div class='kpi-eyebrow'>Tempo de Ciclo</div>
        <div class='kpi-value'>{tc:.1f}<small> min</small></div>
        <div class='kpi-sub'>Por unidade produzida</div>
        <span class='kpi-badge badge-gray'>{conf_label}</span>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class='kpi kpi-amber'>
        <div class='kpi-eyebrow'>Produção / Mês</div>
        <div class='kpi-value'>{prod['producao_esperada']:,}</div>
        <div class='kpi-sub'>Perda est.: {prod['perda_producao']:,} un.</div>
        <span class='kpi-badge badge-amber'>EF. {prod['eficiencia']:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
k5, k6, k7, k8 = st.columns(4)

with k5:
    avg_disp = np.mean([m['disponibilidade'] for m in maquinas]) * 100
    st.markdown(f"""
    <div class='kpi kpi-blue'>
        <div class='kpi-eyebrow'>Disponibilidade Média</div>
        <div class='kpi-value'>{avg_disp:.1f}<small>%</small></div>
        <div class='kpi-sub'>Média das máquinas</div>
    </div>
    """, unsafe_allow_html=True)

with k6:
    mttf_str = f"{mttf:.1f}" if mttf != float('inf') else "∞"
    unit_str = " h" if mttf != float('inf') else ""
    st.markdown(f"""
    <div class='kpi kpi-blue'>
        <div class='kpi-eyebrow'>MTTF do Sistema</div>
        <div class='kpi-value'>{mttf_str}<small>{unit_str}</small></div>
        <div class='kpi-sub'>Mean Time To Failure</div>
    </div>
    """, unsafe_allow_html=True)

with k7:
    st.markdown(f"""
    <div class='kpi kpi-amber'>
        <div class='kpi-eyebrow'>Ciclos Teóricos / Mês</div>
        <div class='kpi-value'>{prod['ciclos_teoricos']:.0f}</div>
        <div class='kpi-sub'>Sem considerar falhas</div>
    </div>
    """, unsafe_allow_html=True)

with k8:
    st.markdown(f"""
    <div class='kpi kpi-red'>
        <div class='kpi-eyebrow'>Falha Empírica — MC</div>
        <div class='kpi-value'>{mc['taxa_falha']*100:.1f}<small>%</small></div>
        <div class='kpi-sub'>Simulação Monte Carlo</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "VISÃO GERAL",
    "GARGALOS",
    "MONTE CARLO",
    "PRODUÇÃO",
    "SÉRIE VS PARALELO",
    "TUTORIAL",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        st.markdown("<div class='tsec'>Confiabilidade do sistema</div>", unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=prob_func * 100,
            number={'suffix': '%', 'font': {'family': 'Anton', 'size': 44, 'color': '#ffffff'}},
            delta={
                'reference': 90, 'relative': False,
                'font': {'size': 12, 'family': 'Space Mono'},
                'valueformat': '.1f', 'suffix': '%',
                'increasing': {'color': C['green']},
                'decreasing': {'color': C['red']},
            },
            gauge={
                'axis': {'range': [0, 100], 'tickfont': {'color': '#555555', 'size': 9, 'family': 'Space Mono'},
                         'ticksuffix': '%', 'dtick': 25},
                'bar': {'color': C['blue'], 'thickness': 0.18},
                'bgcolor': 'rgba(0,0,0,0)',
                'bordercolor': 'rgba(255,255,255,0.06)',
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(255,45,45,0.06)'},
                    {'range': [50, 80], 'color': 'rgba(255,184,0,0.06)'},
                    {'range': [80, 100], 'color': 'rgba(0,87,255,0.06)'},
                ],
                'threshold': {'line': {'color': C['amber'], 'width': 2}, 'thickness': 0.75, 'value': 90},
            },
            title={'text': 'P(Sistema Funciona)', 'font': {'color': '#555555', 'size': 11, 'family': 'Space Mono'}},
        ))
        fig_gauge.update_layout(**LAYOUT, height=290)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_r:
        st.markdown("<div class='tsec'>Perfil comparativo (normalizado)</div>", unsafe_allow_html=True)
        cats = ['T. Operação', 'P. Falha', 'Indisponib.', 'T. Manutenção']

        def norm(vals):
            mn, mx = min(vals), max(vals)
            return [0.5] * len(vals) if mx == mn else [(v - mn) / (mx - mn) for v in vals]

        tops = norm([m['tempo_operacao'] for m in maquinas])
        pfs = norm([m['prob_falha'] for m in maquinas])
        inds = norm([1 - m['disponibilidade'] for m in maquinas])
        tmans = norm([m['tempo_manutencao'] for m in maquinas])

        fig_radar = go.Figure()
        for i, m in enumerate(maquinas):
            v = [tops[i], pfs[i], inds[i], tmans[i], tops[i]]
            c = cats + [cats[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=v, theta=c, fill='toself',
                name=m['nome'],
                line=dict(color=PAL[i % len(PAL)], width=1.5),
                fillcolor='rgba(0,0,0,0)',
            ))
        fig_radar.update_layout(
            **LAYOUT, height=290,
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0, 1], gridcolor=GRID,
                                 tickfont=dict(color='#555555', size=8, family='Space Mono')),
                angularaxis=dict(gridcolor=GRID, tickfont=dict(color='#888888', size=10, family='Space Grotesk')),
            ),
            legend=LEGEND,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("<div class='tsec'>Parâmetros das máquinas</div>", unsafe_allow_html=True)
    df_maq = pd.DataFrame([{
        'Máquina': m['nome'],
        'T. Op. (min)': f"{m['tempo_operacao']:.1f}",
        'P. Falha': f"{m['prob_falha']*100:.1f}%",
        'P. Funcionamento': f"{m['prob_funcionamento']*100:.1f}%",
        'T. Manut. (min)': f"{m['tempo_manutencao']:.1f}",
        'Disponibilidade': f"{m['disponibilidade']*100:.1f}%",
        'MTBF (h)': f"{m['tempo_mtbf']/60:.1f}" if m['tempo_mtbf'] != float('inf') else "∞",
    } for m in maquinas])
    st.dataframe(df_maq, use_container_width=True, hide_index=True)

    st.markdown("<div class='tsec'>Disponibilidade individual</div>", unsafe_allow_html=True)
    disp_vals = [m['disponibilidade'] * 100 for m in maquinas]
    bar_cols = [C['blue'] if v >= 80 else (C['amber'] if v >= 60 else C['red']) for v in disp_vals]

    fig_disp = go.Figure()
    fig_disp.add_trace(go.Bar(
        x=nomes, y=disp_vals,
        marker=dict(color=bar_cols, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in disp_vals],
        textposition='outside',
        textfont=dict(color='#ffffff', size=10, family='Space Mono'),
    ))
    fig_disp.add_hline(y=80, line_dash='dot', line_color=C['amber'], line_width=1.5,
                        annotation_text=" META 80%",
                        annotation_font=dict(color=C['amber'], size=9, family='Space Mono'))
    fig_disp.update_layout(
        **LAYOUT, height=290,
        yaxis=dict(range=[0, 115], ticksuffix='%', gridcolor=GRID, tickfont=dict(color='#555555')),
        xaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
        showlegend=False, bargap=0.4,
    )
    ax(fig_disp)
    st.plotly_chart(fig_disp, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GARGALOS
# ══════════════════════════════════════════════════════════════════════════════

with tab2:
    col_g1, col_g2 = st.columns([1, 1], gap="large")

    with col_g1:
        st.markdown("<div class='tsec'>Gargalos identificados</div>", unsafe_allow_html=True)

        def mk_alert(title, value, desc, kind, lkind):
            return f"""<div class='alert alert-{kind}'>
                <div class='alert-left alert-l-{lkind}'></div>
                <div class='alert-body'>
                    <div class='alert-title'>{title}</div>
                    <div class='alert-value'>{value}</div>
                    <div class='alert-desc'>{desc}</div>
                </div>
            </div>"""

        st.markdown(mk_alert("MÁQUINA MAIS LENTA",
            f"{g_lenta['nome']} — {g_lenta['tempo_operacao']:.1f} min",
            "Limita o throughput da linha inteira", "amber", "amber"), unsafe_allow_html=True)
        st.markdown(mk_alert("MAIOR RISCO DE FALHA",
            f"{g_critica['nome']} — {g_critica['prob_falha']*100:.1f}% probabilidade de falha",
            "Maior probabilidade de interrupção do ciclo", "red", "red"), unsafe_allow_html=True)
        st.markdown(mk_alert("MENOR DISPONIBILIDADE",
            f"{g_indisp['nome']} — {g_indisp['disponibilidade']*100:.1f}% disponível",
            "Passa mais tempo em manutenção", "blue", "blue"), unsafe_allow_html=True)

        st.markdown("<div class='tsec'>Operação vs manutenção ponderada</div>", unsafe_allow_html=True)
        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(
            name='Operação', x=nomes,
            y=[m['tempo_operacao'] for m in maquinas],
            marker=dict(color=C['blue'], line=dict(width=0)),
        ))
        fig_stack.add_trace(go.Bar(
            name='Manutenção ponderada', x=nomes,
            y=[m['prob_falha'] * m['tempo_manutencao'] for m in maquinas],
            marker=dict(color=C['red'], line=dict(width=0)),
        ))
        fig_stack.update_layout(
            **LAYOUT, height=280, barmode='stack',
            yaxis=dict(ticksuffix=' min', gridcolor=GRID, tickfont=dict(color='#555555')),
            xaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
            legend=LEGEND, bargap=0.35,
        )
        ax(fig_stack)
        st.plotly_chart(fig_stack, use_container_width=True)

    with col_g2:
        st.markdown("<div class='tsec'>Impacto de falha individual</div>", unsafe_allow_html=True)
        nomes_imp = [x[0]['nome'] for x in impactos]
        vals_imp = [x[1] * 100 for x in impactos]
        bar_imp = [C['red'] if v > 10 else (C['amber'] if v > 5 else C['blue']) for v in vals_imp]

        fig_imp = go.Figure(go.Bar(
            x=vals_imp, y=nomes_imp, orientation='h',
            marker=dict(color=bar_imp, line=dict(width=0)),
            text=[f"+{v:.2f}%" for v in vals_imp],
            textposition='outside',
            textfont=dict(color='#ffffff', size=10, family='Space Mono'),
        ))
        fig_imp.update_layout(
            **LAYOUT, height=300,
            xaxis=dict(ticksuffix='%', gridcolor=GRID, tickfont=dict(color='#555555')),
            yaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
            showlegend=False,
        )
        ax(fig_imp)
        st.plotly_chart(fig_imp, use_container_width=True)

        st.markdown("<div class='tsec'>Mapa de calor — risco composto</div>", unsafe_allow_html=True)
        z = [[m['prob_falha'] * (1 - m['disponibilidade']) * 100 for m in maquinas]]
        fig_heat = go.Figure(go.Heatmap(
            z=z, x=nomes, y=['RISCO'],
            colorscale=[[0, '#0a0a0a'], [0.4, '#FFB800'], [1, '#FF2D2D']],
            text=[[f"{v:.3f}%" for v in z[0]]],
            texttemplate="%{text}",
            textfont=dict(size=11, family='Space Mono', color='#ffffff'),
            showscale=True,
            colorbar=dict(
                tickfont=dict(color='#555555', size=9, family='Space Mono'),
                ticksuffix='%', len=0.9, thickness=10,
                bgcolor='rgba(0,0,0,0)', bordercolor='#1f1f1f',
            ),
        ))
        fig_heat.update_layout(
            **LAYOUT, height=130,
            xaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
            yaxis=dict(tickfont=dict(color='#555555', family='Space Mono')),
        )
        st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MONTE CARLO
# ══════════════════════════════════════════════════════════════════════════════

with tab3:
    st.markdown("<div class='tsec'>Resultados da simulação Monte Carlo</div>", unsafe_allow_html=True)
    mk1, mk2, mk3, mk4 = st.columns(4)

    with mk1:
        st.markdown(f"""<div class='kpi kpi-green'>
            <div class='kpi-eyebrow'>Taxa de Funcionamento</div>
            <div class='kpi-value'>{mc['taxa_funcionamento']*100:.2f}<small>%</small></div>
            <div class='kpi-sub'>Empírica · {iteracoes_mc:,} iter.</div>
        </div>""", unsafe_allow_html=True)
    with mk2:
        st.markdown(f"""<div class='kpi kpi-red'>
            <div class='kpi-eyebrow'>Taxa de Falha</div>
            <div class='kpi-value'>{mc['taxa_falha']*100:.2f}<small>%</small></div>
            <div class='kpi-sub'>Empírica · {iteracoes_mc:,} iter.</div>
        </div>""", unsafe_allow_html=True)
    with mk3:
        st.markdown(f"""<div class='kpi kpi-blue'>
            <div class='kpi-eyebrow'>Tempo Médio de Ciclo</div>
            <div class='kpi-value'>{mc['tempo_medio_ciclo']:.2f}<small> min</small></div>
            <div class='kpi-sub'>± {mc['desvio_padrao']:.2f} min (dp)</div>
        </div>""", unsafe_allow_html=True)
    with mk4:
        st.markdown(f"""<div class='kpi kpi-amber'>
            <div class='kpi-eyebrow'>Range do Ciclo</div>
            <div class='kpi-value' style='font-size:2rem'>{mc['tempo_minimo']:.1f}<small>–</small>{mc['tempo_maximo']:.1f}</div>
            <div class='kpi-sub'>mín – máx (min)</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_m1, col_m2 = st.columns([3, 2], gap="large")

    with col_m1:
        st.markdown("<div class='tsec'>Distribuição dos tempos de ciclo</div>", unsafe_allow_html=True)
        tempos_arr = np.array(mc['tempos'])
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=tempos_arr, nbinsx=45,
            marker=dict(color=C['blue'], opacity=0.55, line=dict(width=0)),
            name='Frequência',
        ))
        mu, sigma = mc['tempo_medio_ciclo'], mc['desvio_padrao']
        fig_hist.add_vline(x=mu, line_dash='solid', line_color=C['white'], line_width=1.5,
                            annotation_text=f" μ = {mu:.1f}",
                            annotation_font=dict(color=C['white'], size=9, family='Space Mono'))
        fig_hist.add_vline(x=mu + sigma, line_dash='dot', line_color=C['amber'], line_width=1,
                            annotation_text=" +1σ", annotation_font=dict(color=C['amber'], size=9))
        fig_hist.add_vline(x=mu - sigma, line_dash='dot', line_color=C['amber'], line_width=1,
                            annotation_text=" −1σ", annotation_font=dict(color=C['amber'], size=9))
        fig_hist.update_layout(
            **LAYOUT, height=310,
            xaxis=dict(title='Tempo de ciclo (min)', gridcolor=GRID, tickfont=dict(color='#555555', family='Space Mono')),
            yaxis=dict(title='Frequência', gridcolor=GRID, tickfont=dict(color='#555555', family='Space Mono')),
            showlegend=False,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_m2:
        st.markdown("<div class='tsec'>Teórico vs empírico</div>", unsafe_allow_html=True)
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name='Teórico', x=['Funcionamento', 'Falha'],
            y=[prob_func * 100, prob_falha * 100],
            marker=dict(color=C['gray'], opacity=0.7, line=dict(width=0)),
        ))
        fig_comp.add_trace(go.Bar(
            name='Empírico (MC)', x=['Funcionamento', 'Falha'],
            y=[mc['taxa_funcionamento'] * 100, mc['taxa_falha'] * 100],
            marker=dict(color=C['blue'], line=dict(width=0)),
        ))
        fig_comp.update_layout(
            **LAYOUT, height=310, barmode='group',
            yaxis=dict(ticksuffix='%', gridcolor=GRID, tickfont=dict(color='#555555')),
            xaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
            legend=LEGEND, bargap=0.25,
        )
        ax(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("<div class='tsec'>Convergência da taxa de falha</div>", unsafe_allow_html=True)
    random.seed(42)
    passos = np.linspace(10, iteracoes_mc, min(120, iteracoes_mc)).astype(int)
    falhas_seq = []
    acum = 0
    for _ in range(iteracoes_mc):
        acum += (random.random() < prob_falha)
        falhas_seq.append(acum)
    taxas_conv = [(falhas_seq[p - 1] / p) * 100 for p in passos]

    fig_conv = go.Figure()
    fig_conv.add_trace(go.Scatter(
        x=passos, y=taxas_conv, mode='lines',
        line=dict(color=C['blue'], width=2),
        fill='tozeroy',
        fillcolor='rgba(0,87,255,0.05)',
        name='Taxa empírica',
    ))
    fig_conv.add_hline(y=prob_falha * 100, line_dash='dash',
                        line_color=C['red'], line_width=1.5,
                        annotation_text=f" TEÓRICO {prob_falha*100:.2f}%",
                        annotation_font=dict(color=C['red'], size=9, family='Space Mono'))
    fig_conv.update_layout(
        **LAYOUT, height=260,
        xaxis=dict(title='Iterações', gridcolor=GRID, tickfont=dict(color='#555555', family='Space Mono')),
        yaxis=dict(title='Taxa de falha (%)', ticksuffix='%', gridcolor=GRID,
                   tickfont=dict(color='#555555', family='Space Mono')),
        showlegend=False,
    )
    st.plotly_chart(fig_conv, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRODUÇÃO
# ══════════════════════════════════════════════════════════════════════════════

with tab4:
    col_p1, col_p2 = st.columns([1, 1], gap="large")

    with col_p1:
        st.markdown("<div class='tsec'>Produção mensal — waterfall</div>", unsafe_allow_html=True)
        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "total"],
            x=["Ciclos Teóricos", "Perdas por Falha", "Produção Real"],
            y=[prod['ciclos_teoricos'], -prod['perda_producao'], 0],
            connector={"line": {"color": GRID, "width": 1}},
            increasing={"marker": {"color": C['blue'], "line": {"width": 0}}},
            decreasing={"marker": {"color": C['red'], "line": {"width": 0}}},
            totals={"marker": {"color": C['green'], "line": {"width": 0}}},
            text=[f"{prod['ciclos_teoricos']:.0f}", f"−{prod['perda_producao']}", f"{prod['producao_esperada']}"],
            textfont=dict(color='#ffffff', size=11, family='Space Mono'),
        ))
        fig_wf.update_layout(
            **LAYOUT, height=310,
            yaxis=dict(gridcolor=GRID, tickfont=dict(color='#555555')),
            xaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
            showlegend=False,
        )
        ax(fig_wf)
        st.plotly_chart(fig_wf, use_container_width=True)

    with col_p2:
        st.markdown("<div class='tsec'>Produção vs perdas</div>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=['Produção Realizada', 'Perdas por Falha'],
            values=[prod['producao_esperada'], max(prod['perda_producao'], 0)],
            hole=0.65,
            marker=dict(colors=[C['blue'], C['red']], line=dict(color='#000000', width=3)),
            textfont=dict(family='Space Grotesk', size=11, color='#ffffff'),
            hovertemplate='%{label}: %{value} un. (%{percent})<extra></extra>',
        ))
        fig_pie.update_layout(
            **LAYOUT, height=310,
            annotations=[dict(
                text=f"<b>{prod['eficiencia']:.1f}%</b><br>efic.",
                x=0.5, y=0.5,
                font=dict(size=16, color='#ffffff', family='Anton'),
                showarrow=False,
            )],
            legend=LEGEND,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<div class='tsec'>Projeção — 4 semanas</div>", unsafe_allow_html=True)
    semanas = ['SEMANA 1', 'SEMANA 2', 'SEMANA 3', 'SEMANA 4']
    var = np.random.RandomState(7).uniform(0.92, 1.08, 4)
    prods_s = [prod['producao_esperada'] / 4 * v for v in var]
    perdas_s = [prod['perda_producao'] / 4 * v for v in var]

    fig_sem = go.Figure()
    fig_sem.add_trace(go.Bar(name='Produzido', x=semanas, y=prods_s,
                              marker=dict(color=C['blue'], line=dict(width=0))))
    fig_sem.add_trace(go.Bar(name='Perdas', x=semanas, y=perdas_s,
                              marker=dict(color=C['red'], line=dict(width=0))))
    fig_sem.update_layout(
        **LAYOUT, height=270, barmode='stack',
        yaxis=dict(gridcolor=GRID, tickfont=dict(color='#555555')),
        xaxis=dict(tickfont=dict(color='#888888', family='Space Mono', size=9)),
        legend=LEGEND, bargap=0.3,
    )
    ax(fig_sem)
    st.plotly_chart(fig_sem, use_container_width=True)

    st.markdown("<div class='tsec'>Resumo numérico</div>", unsafe_allow_html=True)
    r1, r2, r3, r4, r5 = st.columns(5)
    with r1:
        st.metric("Ciclos Teóricos", f"{prod['ciclos_teoricos']:.0f}")
    with r2:
        st.metric("Ciclos Reais", f"{prod['ciclos_reais']:.0f}")
    with r3:
        st.metric("Produção Esperada", f"{prod['producao_esperada']:,} un.")
    with r4:
        st.metric("Perdas", f"{prod['perda_producao']:,} un.")
    with r5:
        st.metric("Eficiência", f"{prod['eficiencia']:.1f}%",
                   delta=f"{prod['eficiencia']-90:.1f}% vs meta 90%")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SÉRIE vs PARALELO
# ══════════════════════════════════════════════════════════════════════════════

with tab5:
    pf_s, pf_s_ok = calcular_prob_serie(maquinas)
    pf_p, pf_p_ok = calcular_prob_paralelo(maquinas)
    tc_s = calcular_tempo_ciclo(maquinas, 'serie')
    tc_p = calcular_tempo_ciclo(maquinas, 'paralelo')
    prod_s = calcular_producao_esperada(maquinas, 'serie', horas_dia, dias_mes)
    prod_p = calcular_producao_esperada(maquinas, 'paralelo', horas_dia, dias_mes)

    st.markdown("<div class='tsec'>Comparação direta</div>", unsafe_allow_html=True)
    cv1, cv2, cv3 = st.columns(3)

    def compare_card(label, val_s, val_p, unit_s, unit_p, winner):
        cor_s = "#0057FF"
        cor_p = "#ffffff"
        return f"""<div class='compare-card'>
            <div class='compare-eyebrow'>{label}</div>
            <div class='compare-row'>
                <div class='compare-side'>
                    <div class='compare-side-label' style='color:#0057FF'>SÉRIE</div>
                    <div class='compare-val' style='color:{cor_s}'>{val_s}<span style='font-size:1rem;color:#555'>{unit_s}</span></div>
                </div>
                <div class='compare-vs'>VS</div>
                <div class='compare-side'>
                    <div class='compare-side-label' style='color:#888'>PARALELO</div>
                    <div class='compare-val' style='color:{cor_p}'>{val_p}<span style='font-size:1rem;color:#555'>{unit_p}</span></div>
                </div>
            </div>
            <div class='compare-winner'>► {winner.upper()} É MELHOR NESTE CRITÉRIO</div>
        </div>"""

    with cv1:
        w = "Paralelo" if pf_p_ok > pf_s_ok else "Série"
        st.markdown(compare_card("Confiabilidade",
            f"{pf_s_ok*100:.1f}", f"{pf_p_ok*100:.1f}", "%", "%", w), unsafe_allow_html=True)
    with cv2:
        w = "Paralelo" if tc_p < tc_s else "Série"
        st.markdown(compare_card("Tempo de Ciclo",
            f"{tc_s:.1f}", f"{tc_p:.1f}", " min", " min", w), unsafe_allow_html=True)
    with cv3:
        w = "Paralelo" if prod_p['producao_esperada'] > prod_s['producao_esperada'] else "Série"
        st.markdown(compare_card("Produção / Mês",
            f"{prod_s['producao_esperada']:,}", f"{prod_p['producao_esperada']:,}", "", "", w), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_sp1, col_sp2 = st.columns([1, 1], gap="large")

    with col_sp1:
        st.markdown("<div class='tsec'>Confiabilidade vs risco</div>", unsafe_allow_html=True)
        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(name='Série', x=['Confiabilidade (%)', 'Risco de Falha (%)'],
                                   y=[pf_s_ok * 100, pf_s * 100],
                                   marker=dict(color=C['blue'], line=dict(width=0))))
        fig_bars.add_trace(go.Bar(name='Paralelo', x=['Confiabilidade (%)', 'Risco de Falha (%)'],
                                   y=[pf_p_ok * 100, pf_p * 100],
                                   marker=dict(color=C['gray'], line=dict(width=0))))
        fig_bars.update_layout(
            **LAYOUT, height=295, barmode='group',
            yaxis=dict(ticksuffix='%', gridcolor=GRID, tickfont=dict(color='#555555')),
            xaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
            legend=LEGEND, bargap=0.25,
        )
        ax(fig_bars)
        st.plotly_chart(fig_bars, use_container_width=True)

    with col_sp2:
        st.markdown("<div class='tsec'>Produção: teórica vs realizada</div>", unsafe_allow_html=True)
        fig_pc = go.Figure()
        fig_pc.add_trace(go.Bar(name='Teórico', x=['Série', 'Paralelo'],
                                 y=[prod_s['ciclos_teoricos'], prod_p['ciclos_teoricos']],
                                 marker=dict(color=C['gray'], opacity=0.4, line=dict(width=0))))
        fig_pc.add_trace(go.Bar(name='Realizado', x=['Série', 'Paralelo'],
                                 y=[prod_s['producao_esperada'], prod_p['producao_esperada']],
                                 marker=dict(color=C['blue'], line=dict(width=0))))
        fig_pc.update_layout(
            **LAYOUT, height=295, barmode='overlay',
            yaxis=dict(gridcolor=GRID, tickfont=dict(color='#555555')),
            xaxis=dict(tickfont=dict(color='#888888', family='Space Grotesk')),
            legend=LEGEND, bargap=0.3,
        )
        ax(fig_pc)
        st.plotly_chart(fig_pc, use_container_width=True)

    st.markdown("<div class='tsec'>Tabela comparativa completa</div>", unsafe_allow_html=True)
    df_comp = pd.DataFrame({
        'Métrica': ['Confiabilidade', 'Risco de Falha', 'Tempo de Ciclo', 'Produção/mês', 'Perdas/mês', 'Eficiência'],
        'Série': [f"{pf_s_ok*100:.2f}%", f"{pf_s*100:.2f}%", f"{tc_s:.1f} min",
                  f"{prod_s['producao_esperada']:,} un.", f"{prod_s['perda_producao']:,} un.", f"{prod_s['eficiencia']:.1f}%"],
        'Paralelo': [f"{pf_p_ok*100:.2f}%", f"{pf_p*100:.2f}%", f"{tc_p:.1f} min",
                     f"{prod_p['producao_esperada']:,} un.", f"{prod_p['perda_producao']:,} un.", f"{prod_p['eficiencia']:.1f}%"],
        'Melhor': [
            "► PARALELO" if pf_p_ok > pf_s_ok else "► SÉRIE",
            "► PARALELO" if pf_p < pf_s else "► SÉRIE",
            "► PARALELO" if tc_p < tc_s else "► SÉRIE",
            "► PARALELO" if prod_p['producao_esperada'] > prod_s['producao_esperada'] else "► SÉRIE",
            "► PARALELO" if prod_p['perda_producao'] < prod_s['perda_producao'] else "► SÉRIE",
            "► PARALELO" if prod_p['eficiencia'] > prod_s['eficiencia'] else "► SÉRIE",
        ],
    })
    st.dataframe(df_comp, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — TUTORIAL
# ══════════════════════════════════════════════════════════════════════════════

with tab6:
    st.markdown("<div class='tsec'>Como usar o SimProd</div>", unsafe_allow_html=True)

    passos = [
        ("01", "Escolha a topologia da linha",
         "No bloco <b>Configuração Geral</b>, defina se as máquinas trabalham em "
         "<b>Série</b> (uma depende da outra, sequencialmente) ou em <b>Paralelo</b> "
         "(funcionam ao mesmo tempo, de forma independente). Ajuste também horas por dia, "
         "dias por mês e o número de iterações da simulação Monte Carlo."),
        ("02", "Monte a linha de produção",
         "Em <b>Máquinas da Linha</b>, clique em <b>➕ Adicionar Máquina</b> — escolha um "
         "perfil pronto (leve, padrão, pesada, crítica, antiga) para já começar com valores "
         "realistas, ou ajuste manualmente depois."),
        ("03", "Ajuste cada máquina",
         "Abra o cartão de uma máquina para editar nome, ativá-la ou desativá-la, aplicar um "
         "novo perfil, e usar os controles deslizantes de tempo de operação, probabilidade de "
         "falha e tempo de manutenção. Máquinas desativadas não entram no cálculo."),
        ("04", "Execute a simulação",
         "Clique em <b>▶ Executar Simulação</b> para recalcular os indicadores com os "
         "parâmetros atuais. Os cartões de resumo e os indicadores no topo da página são "
         "atualizados automaticamente a cada alteração."),
        ("05", "Leia os resultados",
         "Os indicadores no topo (Confiabilidade, Risco de Falha, Tempo de Ciclo, Produção/Mês "
         "etc.) resumem o estado da linha. Nas abas abaixo, explore os detalhes: visão geral, "
         "gargalos, simulação Monte Carlo, produção e a comparação entre série e paralelo."),
    ]
    for num, titulo, desc in passos:
        st.markdown(f"""
        <div class='tut-step'>
            <div class='tut-num'>{num}</div>
            <div class='tut-body'>
                <div class='tut-title'>{titulo}</div>
                <div class='tut-desc'>{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='tsec'>Série vs paralelo — a diferença</div>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2, gap="large")
    with col_t1:
        st.markdown("""
        <div class='alert alert-blue'>
            <div class='alert-left alert-l-blue'></div>
            <div class='alert-body'>
                <div class='alert-title'>SÉRIE</div>
                <div class='alert-desc'>
                    O produto passa por todas as máquinas, uma depois da outra. Se qualquer
                    uma falhar, a linha inteira para. O tempo de ciclo é a <b>soma</b> dos
                    tempos de cada máquina — mais lento, porém mais previsível quando todas
                    as máquinas são confiáveis.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown("""
        <div class='alert alert-amber'>
            <div class='alert-left alert-l-amber'></div>
            <div class='alert-body'>
                <div class='alert-title'>PARALELO</div>
                <div class='alert-desc'>
                    As máquinas trabalham ao mesmo tempo, de forma independente. A linha só
                    falha se <b>todas</b> falharem juntas. O tempo de ciclo é o <b>maior</b>
                    tempo entre as máquinas — geralmente mais rápido e mais tolerante a falhas.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='tsec'>Glossário de indicadores</div>", unsafe_allow_html=True)
    glossario = [
        ("CONFIABILIDADE", "Probabilidade de o sistema completo funcionar sem falhas em um ciclo."),
        ("RISCO DE FALHA", "Probabilidade complementar: chance de o sistema falhar em um ciclo."),
        ("TEMPO DE CICLO", "Tempo para produzir uma unidade — soma (série) ou máximo (paralelo) dos tempos de cada máquina."),
        ("PRODUÇÃO / MÊS", "Estimativa de unidades produzidas no período configurado, já descontando as falhas esperadas."),
        ("DISPONIBILIDADE", "Fração do tempo em que uma máquina está operando, e não em manutenção."),
        ("MTBF", "Mean Time Between Failures — tempo médio entre uma falha e outra da máquina."),
        ("MTTF DO SISTEMA", "Mean Time To Failure — tempo médio esperado até a primeira falha do sistema completo."),
        ("MONTE CARLO", "Simulação que roda milhares de ciclos aleatórios (conforme as probabilidades definidas) para validar, na prática, os números calculados pela teoria."),
        ("GARGALO", "A máquina mais lenta, mais propensa a falhar, ou com menor disponibilidade — o ponto que mais limita a linha."),
    ]
    for termo, definicao in glossario:
        st.markdown(f"""
        <div class='tut-glossary-row'>
            <div class='tut-glossary-term'>{termo}</div>
            <div class='tut-glossary-def'>{definicao}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='tsec'>Roteiro das abas</div>", unsafe_allow_html=True)
    df_abas = pd.DataFrame([
        {"Aba": "VISÃO GERAL", "Conteúdo": "Gauge de confiabilidade, radar comparativo entre máquinas, tabela de parâmetros e disponibilidade individual."},
        {"Aba": "GARGALOS", "Conteúdo": "Alertas com a máquina mais lenta, mais crítica e menos disponível, impacto de cada falha e mapa de calor de risco."},
        {"Aba": "MONTE CARLO", "Conteúdo": "Resultados empíricos da simulação: distribuição dos tempos de ciclo, comparação teórico vs empírico e convergência da taxa de falha."},
        {"Aba": "PRODUÇÃO", "Conteúdo": "Waterfall e pizza de produção vs perdas, projeção semanal e resumo numérico do mês."},
        {"Aba": "SÉRIE VS PARALELO", "Conteúdo": "Comparação lado a lado das duas topologias com os mesmos dados de máquina, mostrando qual vence em cada critério."},
    ])
    st.dataframe(df_abas, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='footer'>
    <span><strong>SIMPROD</strong> · SIMULADOR DE LINHA DE PRODUÇÃO</span>
    <span>ALGORITMOS E PROG. COMPUTACIONAL · PROF. DR. JOSÉ A. SALIM</span>
</div>
""", unsafe_allow_html=True)
