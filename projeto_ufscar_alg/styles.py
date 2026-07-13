"""
Estilos CSS do dashboard SimProd.

Mantém toda a folha de estilo separada da lógica da aplicação,
para facilitar ajustes visuais sem mexer no restante do código.
"""

import streamlit as st

CSS_STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    :root {
        --black:      #000000;
        --white:      #ffffff;
        --gray-950:   #0a0a0a;
        --gray-900:   #111111;
        --gray-800:   #1a1a1a;
        --gray-700:   #222222;
        --gray-600:   #2e2e2e;
        --gray-400:   #6b6b6b;
        --gray-300:   #9a9a9a;
        --gray-200:   #b0b0b0;
        --gray-100:   #d4d4d4;
        --gray-50:    #ebebeb;
        --blue:       #0057FF;
        --blue-dim:   rgba(0,87,255,0.12);
        --blue-mid:   rgba(0,87,255,0.35);
        --red:        #FF2D2D;
        --amber:      #FFB800;
        --green:      #00C46A;
        --border:     #1f1f1f;
        --border-hi:  #3a3a3a;
        --text:       #ffffff;
        --text-2:     #b0b0b0;
        --text-3:     #555555;
        --cut: 16px;
    }

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text);
    }

    /* Fundo real — Streamlit define isso nesses containers específicos,
       não em body/html, e reaplica sua própria cor depois do nosso CSS
       se não formos igualmente específicos aqui. */
    html, body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stBottomBlockContainer"],
    section.main,
    .main > div:first-child {
        background-color: var(--black) !important;
        background: var(--black) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stDecoration"] { background: var(--blue) !important; height: 3px !important; }
    [data-testid="stToolbar"] { background: transparent !important; }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none; }
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }

    /* Popovers/dropdowns (selectbox, select_slider) renderizam fora da
       árvore normal — precisam de seletores próprios e !important pra
       não herdar o branco padrão do BaseWeb. */
    div[data-baseweb="popover"] div[role="listbox"],
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background: var(--gray-900) !important;
        border: 2px solid var(--border-hi) !important;
        border-radius: 0 !important;
    }
    div[data-baseweb="popover"] li,
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        background: var(--gray-900) !important;
        color: var(--white) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    div[data-baseweb="popover"] li:hover,
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
        background: var(--blue-dim) !important;
        color: var(--white) !important;
    }
    div[data-baseweb="popover"] li[aria-selected="true"] {
        background: var(--blue) !important;
        color: var(--black) !important;
    }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--black); }
    ::-webkit-scrollbar-thumb { background: var(--gray-600); }

    /* ══ MASTHEAD ═══════════════════════════════════════════════ */
    .masthead {
        background: var(--black);
        border-bottom: 3px solid var(--white);
        padding: 20px 0 18px;
        margin-bottom: 0;
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
    }
    .masthead-left { display: flex; align-items: flex-end; gap: 20px; }
    .masthead-logo {
        font-family: 'Anton', sans-serif;
        font-size: 3.4rem;
        line-height: 0.9;
        color: var(--white);
        letter-spacing: -1px;
    }
    .masthead-logo span {
        color: var(--black);
        background: var(--blue);
        padding: 0 10px;
        margin-left: 2px;
        display: inline-block;
    }
    .masthead-rule {
        width: 5px;
        height: 42px;
        background: var(--blue);
        flex-shrink: 0;
        margin-bottom: 4px;
    }
    .masthead-sub {
        font-size: 0.74rem;
        font-weight: 500;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--gray-300);
        line-height: 1.5;
    }
    .masthead-sub strong { color: var(--blue); font-weight: 700; }
    .masthead-tag {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        color: var(--gray-400);
        letter-spacing: 1.5px;
        text-align: right;
    }

    /* ══ SECTION LABEL ══════════════════════════════════════════ */
    .sec-label {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 30px 0 16px;
    }
    .sec-num {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        color: var(--black);
        letter-spacing: 2px;
        background: var(--blue);
        border-radius: 999px;
        padding: 5px 12px;
        flex-shrink: 0;
    }
    .sec-title {
        font-family: 'Anton', sans-serif;
        font-size: 1.25rem;
        letter-spacing: 0.5px;
        color: var(--white);
    }
    .sec-line {
        flex: 1;
        height: 2px;
        background: var(--border-hi);
    }

    /* ══ CONFIG STRIP ════════════════════════════════════════════ */
    .config-strip {
        background: var(--gray-900);
        border: 2px solid var(--border-hi);
        border-left: 6px solid var(--blue);
        padding: 20px 22px 12px;
        margin-bottom: 0;
    }

    /* ══ KPI CARDS ═══════════════════════════════════════════════ */
    .kpi {
        background: var(--gray-900);
        border: 2px solid var(--border-hi);
        border-top: 6px solid var(--border-hi);
        padding: 22px 20px 18px;
        position: relative;
        height: 100%;
        clip-path: polygon(0 0, calc(100% - var(--cut)) 0, 100% var(--cut), 100% 100%, 0 100%);
        transition: border-color 0.15s, transform 0.15s;
    }
    .kpi:hover { border-color: var(--gray-300); transform: translateY(-2px); }
    .kpi-blue  { border-top-color: var(--blue);  }
    .kpi-red   { border-top-color: var(--red);   }
    .kpi-amber { border-top-color: var(--amber); }
    .kpi-green { border-top-color: var(--green); }

    .kpi-eyebrow {
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--gray-300);
        margin-bottom: 10px;
    }
    .kpi-value {
        font-family: 'Anton', sans-serif;
        font-size: 3rem;
        line-height: 0.95;
        color: var(--white);
        letter-spacing: -1px;
    }
    .kpi-value small {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        color: var(--gray-300);
        font-weight: 400;
        letter-spacing: 0;
    }
    .kpi-sub {
        font-size: 0.73rem;
        color: var(--gray-400);
        margin-top: 10px;
        letter-spacing: 0.3px;
    }
    .kpi-badge {
        display: inline-block;
        font-family: 'Space Mono', monospace;
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 4px 12px;
        margin-top: 12px;
        border-radius: 999px;
    }
    .badge-blue  { background: var(--blue);  color: var(--black); }
    .badge-red   { background: var(--red);   color: var(--black); }
    .badge-amber { background: var(--amber); color: var(--black); }
    .badge-green { background: var(--green); color: var(--black); }
    .badge-gray  { background: var(--gray-100); color: var(--black); }

    /* ══ MACHINE CARDS ═══════════════════════════════════════════ */
    .mcard {
        background: var(--gray-900);
        border: 2px solid var(--border-hi);
        padding: 16px;
        height: 100%;
        clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
        transition: border-color 0.15s;
    }
    .mcard:hover { border-color: var(--gray-300); }
    .mcard-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--border);
    }
    .mcard-accent { width: 6px; height: 30px; flex-shrink: 0; }
    .mcard-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
        color: var(--white);
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .mcard-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        font-size: 0.73rem;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    .mcard-row:last-child { border-bottom: none; }
    .mcard-row span { color: var(--gray-400); letter-spacing: 0.3px; }
    .mcard-row b {
        font-family: 'Space Mono', monospace;
        color: var(--white);
        font-weight: 400;
        font-size: 0.75rem;
    }

    /* ══ ALERT CARDS ═════════════════════════════════════════════ */
    .alert {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border: 2px solid;
    }
    .alert-blue  { background: var(--blue-dim);          border-color: var(--blue); }
    .alert-red   { background: rgba(255,45,45,0.07);     border-color: var(--red); }
    .alert-amber { background: rgba(255,184,0,0.07);     border-color: var(--amber); }
    .alert-left  { width: 4px; flex-shrink: 0; align-self: stretch; }
    .alert-l-blue  { background: var(--blue);  }
    .alert-l-red   { background: var(--red);   }
    .alert-l-amber { background: var(--amber); }
    .alert-body  { flex: 1; }
    .alert-title { font-size: 0.78rem; font-weight: 700; color: var(--white); text-transform: uppercase; letter-spacing: 0.8px; }
    .alert-value { font-family: 'Space Mono', monospace; font-size: 0.74rem; color: var(--gray-200); margin-top: 3px; }
    .alert-desc  { font-size: 0.69rem; color: var(--gray-400); margin-top: 3px; letter-spacing: 0.2px; }

    /* ══ SECTION HEADER (tab interno) ═══════════════════════════ */
    .tsec {
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--gray-300);
        padding: 24px 0 12px;
    }
    .tsec::before {
        content: '';
        width: 8px; height: 8px;
        background: var(--blue);
        flex-shrink: 0;
    }
    .tsec::after { content: ''; flex: 1; height: 1px; background: var(--border); }

    /* ══ COMPARE CARDS ═══════════════════════════════════════════ */
    .compare-card {
        background: var(--gray-900);
        border: 2px solid var(--border-hi);
        border-top: 6px solid var(--border-hi);
        padding: 20px;
        clip-path: polygon(0 0, calc(100% - var(--cut)) 0, 100% var(--cut), 100% 100%, 0 100%);
    }
    .compare-eyebrow {
        font-family: 'Space Mono', monospace;
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--gray-300);
        margin-bottom: 18px;
    }
    .compare-row { display: flex; align-items: flex-end; gap: 12px; }
    .compare-side { text-align: center; flex: 1; }
    .compare-side-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.6rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .compare-val {
        font-family: 'Anton', sans-serif;
        font-size: 1.7rem;
        line-height: 1;
        letter-spacing: 0;
    }
    .compare-vs {
        font-family: 'Space Mono', monospace;
        font-size: 0.6rem;
        color: var(--gray-400);
        letter-spacing: 2px;
        padding: 0 4px;
    }
    .compare-winner {
        font-size: 0.7rem;
        color: var(--gray-200);
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid var(--border);
        font-family: 'Space Mono', monospace;
        letter-spacing: 0.5px;
    }

    /* ══ EMPTY STATE ══════════════════════════════════════════════ */
    .empty-state {
        text-align: center;
        padding: 56px 24px;
        background: var(--gray-900);
        border: 2px solid var(--border-hi);
        border-left: 6px solid var(--blue);
        color: var(--gray-400);
    }
    .empty-title {
        font-family: 'Anton', sans-serif;
        font-size: 1.5rem;
        color: var(--white);
        letter-spacing: 1px;
        margin-bottom: 6px;
    }

    /* ══ MACHINE PICKER (novo) ══════════════════════════════════ */
    .picker-strip {
        background: var(--gray-900);
        border: 2px solid var(--border-hi);
        border-left: 6px solid var(--blue);
        padding: 4px 22px 18px;
    }
    .picker-hint {
        font-size: 0.72rem;
        color: var(--gray-400);
        letter-spacing: 0.3px;
        padding: 14px 0 4px;
    }
    .preset-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--gray-300);
        padding: 4px 0 8px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 5px 12px;
        border-radius: 999px;
        background: var(--gray-800);
        color: var(--gray-200);
        border: 1px solid var(--border-hi);
        margin-bottom: 10px;
    }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; }

    /* ══ STREAMLIT OVERRIDES ══════════════════════════════════════ */
    .stSlider > div > div > div > div { background: var(--blue) !important; }
    .stSlider [role="slider"] { background: var(--white) !important; border: 2px solid var(--blue) !important; }

    /* Valor flutuante acima do controle deslizante (aparece em sliders
       e em select_slider) — o Streamlit usa a cor "primária" padrão
       (vermelho) aqui por default, o que destoa do resto do sistema.
       Forçamos a mesma paleta usada em todo o dashboard. */
    [data-testid="stThumbValue"],
    [data-testid="stTickBarMin"],
    [data-testid="stTickBarMax"],
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: var(--white) !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
    }
    [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {
        color: var(--gray-400) !important;
        font-weight: 400 !important;
    }

    /* Toggle (liga/desliga) — mesma lógica: neutraliza a cor primária
       padrão do Streamlit e usa azul/cinza do sistema. */
    [data-testid="stToggle"] label div[data-baseweb="checkbox"] div:first-child {
        background: var(--gray-700) !important;
        border-color: var(--border-hi) !important;
    }
    [data-testid="stToggle"] input:checked ~ div[data-baseweb="checkbox"] div:first-child,
    [data-testid="stToggle"] label div[data-baseweb="checkbox"] div[aria-checked="true"] {
        background: var(--blue) !important;
    }

    /* Checkbox / radio — mesma unificação de cor primária */
    .stCheckbox [data-baseweb="checkbox"] span,
    .stRadio [data-baseweb="radio"] span {
        border-color: var(--border-hi) !important;
    }
    .stCheckbox [aria-checked="true"] span,
    .stRadio [aria-checked="true"] span {
        background: var(--blue) !important;
        border-color: var(--blue) !important;
    }

    /* Spinner de carregamento — troca o vermelho padrão pelo azul do sistema */
    .stSpinner > div { border-top-color: var(--blue) !important; }

    div[data-baseweb="input"] input,
    .stNumberInput input {
        background: var(--gray-900) !important;
        border: 2px solid var(--border-hi) !important;
        border-radius: 0 !important;
        color: var(--white) !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    div[data-baseweb="input"] input:focus,
    .stNumberInput input:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 1px var(--blue) !important;
    }

    div[data-baseweb="select"] > div {
        background: var(--gray-900) !important;
        border: 2px solid var(--border-hi) !important;
        border-radius: 0 !important;
        color: var(--white) !important;
    }

    label {
        color: var(--gray-200) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        font-family: 'Space Mono', monospace !important;
    }

    .stButton > button {
        background: var(--blue) !important;
        color: var(--black) !important;
        font-family: 'Anton', sans-serif !important;
        font-size: 1rem !important;
        letter-spacing: 2px !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 15px 24px !important;
        width: 100%;
        transition: background 0.15s !important;
        box-shadow: none !important;
        text-transform: uppercase !important;
    }
    .stButton > button:hover {
        background: var(--white) !important;
        color: var(--black) !important;
        transform: none !important;
        box-shadow: none !important;
        filter: none !important;
    }

    /* botões secundários (remover, presets) — menores e discretos */
    .stButton.secondary-btn > button,
    button[kind="secondary"] {
        background: transparent !important;
        color: var(--gray-200) !important;
        border: 2px solid var(--border-hi) !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.68rem !important;
        letter-spacing: 1.5px !important;
        padding: 9px 16px !important;
    }
    button[kind="secondary"]:hover {
        border-color: var(--red) !important;
        color: var(--red) !important;
        background: rgba(255,45,45,0.06) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--gray-900) !important;
        border-radius: 0 !important;
        padding: 6px !important;
        gap: 4px !important;
        border: 2px solid var(--border-hi) !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px !important;
        color: var(--gray-400) !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        padding: 10px 18px !important;
        border-bottom: none !important;
        transition: all 0.1s !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--blue) !important;
        color: var(--black) !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        color: var(--gray-200) !important;
        background: rgba(255,255,255,0.05) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 0 !important;
        background: transparent !important;
    }

    div[data-testid="metric-container"] {
        background: var(--gray-900) !important;
        border: 2px solid var(--border-hi) !important;
        border-radius: 0 !important;
        border-top: 4px solid var(--blue) !important;
        padding: 14px 16px !important;
    }
    div[data-testid="metric-container"] label {
        font-size: 0.6rem !important;
        letter-spacing: 2px !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Anton', sans-serif !important;
        font-size: 1.6rem !important;
        color: var(--white) !important;
        letter-spacing: 0 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-family: 'Space Mono', monospace !important;
        font-size: 0.65rem !important;
    }

    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        border-radius: 0 !important;
        border: 2px solid var(--border-hi) !important;
    }

    /* Expander (cartão de máquina editável) */
    [data-testid="stExpander"] {
        background: var(--gray-900) !important;
        border: 2px solid var(--border-hi) !important;
        border-radius: 0 !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.4px !important;
    }

    /* Tutorial */
    .tut-step {
        display: flex;
        gap: 16px;
        padding: 16px 0;
        border-bottom: 1px solid var(--border);
    }
    .tut-step:last-child { border-bottom: none; }
    .tut-num {
        font-family: 'Anton', sans-serif;
        font-size: 1.6rem;
        color: var(--blue);
        flex-shrink: 0;
        width: 40px;
    }
    .tut-body { flex: 1; }
    .tut-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--white);
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 4px;
    }
    .tut-desc {
        font-size: 0.78rem;
        color: var(--gray-300);
        line-height: 1.6;
    }
    .tut-glossary-row {
        display: flex;
        gap: 16px;
        padding: 12px 0;
        border-bottom: 1px solid var(--border);
        align-items: baseline;
    }
    .tut-glossary-row:last-child { border-bottom: none; }
    .tut-glossary-term {
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--blue);
        width: 220px;
        flex-shrink: 0;
        letter-spacing: 0.5px;
    }
    .tut-glossary-def {
        font-size: 0.78rem;
        color: var(--gray-300);
        line-height: 1.5;
    }

    /* Footer */
    .footer {
        margin-top: 56px;
        padding: 22px 0;
        border-top: 3px solid var(--white);
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem;
        color: var(--gray-400);
        letter-spacing: 1px;
    }
    .footer strong { color: var(--white); letter-spacing: 2px; }
</style>
"""


def apply_styles():
    """Injeta a folha de estilo CSS no app Streamlit."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
