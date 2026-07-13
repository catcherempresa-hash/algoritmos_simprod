"""
Gerenciamento do st.session_state: lista de máquinas e presets rápidos.
"""

import streamlit as st

# Presets rápidos — perfis típicos de máquina que o operador pode aplicar
# com um clique, sem precisar saber os números "de cor".
PRESETS = {
    "Leve · rápida e confiável": {"tempo_operacao": 8.0, "prob_falha": 0.02, "tempo_manutencao": 15.0},
    "Padrão · uso geral": {"tempo_operacao": 12.0, "prob_falha": 0.05, "tempo_manutencao": 30.0},
    "Pesada · lenta e robusta": {"tempo_operacao": 25.0, "prob_falha": 0.04, "tempo_manutencao": 45.0},
    "Crítica · alto risco de falha": {"tempo_operacao": 15.0, "prob_falha": 0.15, "tempo_manutencao": 60.0},
    "Antiga · lenta e instável": {"tempo_operacao": 30.0, "prob_falha": 0.20, "tempo_manutencao": 90.0},
}
PRESET_LABELS = list(PRESETS.keys())
PRESET_PLACEHOLDER = "— manter valores —"


def init_state():
    """Inicializa o session_state com a lista de máquinas padrão, se ainda não existir."""
    if 'maquinas_lista' not in st.session_state:
        st.session_state.maquinas_lista = [
            {"id": 0, "ativa": True, "nome": "Máquina 1", "tempo_operacao": 10.0, "prob_falha": 0.05, "tempo_manutencao": 30.0},
            {"id": 1, "ativa": True, "nome": "Máquina 2", "tempo_operacao": 15.0, "prob_falha": 0.07, "tempo_manutencao": 40.0},
            {"id": 2, "ativa": True, "nome": "Máquina 3", "tempo_operacao": 20.0, "prob_falha": 0.09, "tempo_manutencao": 50.0},
        ]
    if 'proximo_id' not in st.session_state:
        st.session_state.proximo_id = 3


def adicionar_maquina(preset_label=None):
    """Adiciona uma nova máquina à lista, opcionalmente a partir de um preset."""
    novo_id = st.session_state.proximo_id
    st.session_state.proximo_id += 1
    valores = PRESETS[preset_label] if preset_label else PRESETS["Padrão · uso geral"]
    st.session_state.maquinas_lista.append({
        "id": novo_id,
        "ativa": True,
        "nome": f"Máquina {novo_id + 1}",
        "tempo_operacao": valores["tempo_operacao"],
        "prob_falha": valores["prob_falha"],
        "tempo_manutencao": valores["tempo_manutencao"],
    })


def remover_maquina(maquina_id):
    """Remove uma máquina da lista pelo seu id."""
    st.session_state.maquinas_lista = [
        m for m in st.session_state.maquinas_lista if m["id"] != maquina_id
    ]


def aplicar_preset(maquina_id, preset_label):
    """Aplica os valores de um preset a uma máquina específica."""
    valores = PRESETS[preset_label]
    for m in st.session_state.maquinas_lista:
        if m["id"] == maquina_id:
            m["tempo_operacao"] = valores["tempo_operacao"]
            m["prob_falha"] = valores["prob_falha"]
            m["tempo_manutencao"] = valores["tempo_manutencao"]
