"""
Lógica de negócio do simulador SimProd.

Contém todos os cálculos de confiabilidade, gargalos, produção e a
simulação de Monte Carlo. Nenhuma função aqui depende do Streamlit —
isso permite testar a lógica isoladamente (ex.: com pytest) sem
precisar rodar o app.
"""

import random
import statistics


def criar_maquina(nome, tempo_operacao, prob_falha, tempo_manutencao):
    """Monta o dicionário de uma máquina, já com métricas derivadas."""
    denom = tempo_operacao + prob_falha * tempo_manutencao
    disponibilidade = tempo_operacao / denom if denom > 0 else 1.0
    mtbf = (tempo_operacao / prob_falha) if prob_falha > 0 else float('inf')
    return {
        'nome': nome,
        'tempo_operacao': tempo_operacao,
        'prob_falha': prob_falha,
        'prob_funcionamento': 1 - prob_falha,
        'tempo_manutencao': tempo_manutencao,
        'disponibilidade': disponibilidade,
        'tempo_mtbf': mtbf,
    }


def calcular_prob_serie(maquinas):
    """Probabilidade de falha/funcionamento para máquinas em série."""
    pf = 1.0
    for m in maquinas:
        pf *= m['prob_funcionamento']
    return 1 - pf, pf


def calcular_prob_paralelo(maquinas):
    """Probabilidade de falha/funcionamento para máquinas em paralelo."""
    pf = 1.0
    for m in maquinas:
        pf *= m['prob_falha']
    return pf, 1 - pf


def calcular_tempo_ciclo(maquinas, config):
    """Tempo de ciclo: soma (série) ou máximo (paralelo)."""
    if config == 'serie':
        return sum(m['tempo_operacao'] for m in maquinas)
    return max(m['tempo_operacao'] for m in maquinas)


def calcular_mttf(maquinas, config):
    """Mean Time To Failure do sistema completo, em horas."""
    if not maquinas:
        return 0
    if config == 'serie':
        taxa = sum(m['prob_falha'] / m['tempo_operacao'] for m in maquinas if m['tempo_operacao'] > 0)
        mttf = 1 / taxa if taxa > 0 else float('inf')
    else:
        pf = 1.0
        for m in maquinas:
            pf *= m['prob_falha']
        mttf = 1 / pf if pf > 0 else float('inf')
    return mttf / 60 if mttf != float('inf') else mttf


def identificar_gargalos(maquinas):
    """Retorna a máquina mais lenta, a mais propensa a falhar e a menos disponível."""
    idx_lenta = max(range(len(maquinas)), key=lambda i: maquinas[i]['tempo_operacao'])
    idx_critica = max(range(len(maquinas)), key=lambda i: maquinas[i]['prob_falha'])
    idx_indisponivel = min(range(len(maquinas)), key=lambda i: maquinas[i]['disponibilidade'])
    return maquinas[idx_lenta], maquinas[idx_critica], maquinas[idx_indisponivel]


def analisar_impacto_falha(maquinas, config):
    """Para cada máquina, calcula o quanto sua remoção mudaria a prob. de falha do sistema."""
    if config == 'serie':
        prob_total, _ = calcular_prob_serie(maquinas)
    else:
        prob_total, _ = calcular_prob_paralelo(maquinas)

    impactos = []
    for i, maquina in enumerate(maquinas):
        restantes = [m for j, m in enumerate(maquinas) if j != i]
        if restantes:
            if config == 'serie':
                pf, _ = calcular_prob_serie(restantes)
            else:
                pf, _ = calcular_prob_paralelo(restantes)
        else:
            pf = 0
        impactos.append((maquina, prob_total - pf))

    impactos.sort(key=lambda x: x[1], reverse=True)
    return impactos


def simular_monte_carlo(maquinas, config, iteracoes=5000):
    """Roda a simulação de Monte Carlo e devolve as métricas empíricas."""
    random.seed(42)
    falhas = 0
    tempos = []

    for _ in range(iteracoes):
        falha_serie = False
        todas_falham = True
        tempo = 0
        for m in maquinas:
            f = random.random() < m['prob_falha']
            if config == 'serie':
                if f:
                    falha_serie = True
                tempo += m['tempo_operacao']
            else:
                if not f:
                    todas_falham = False
                tempo = max(tempo, m['tempo_operacao'])

        if config == 'serie':
            if falha_serie:
                falhas += 1
        else:
            if todas_falham:
                falhas += 1

        tempos.append(tempo)

    return {
        'taxa_falha': falhas / iteracoes,
        'taxa_funcionamento': 1 - falhas / iteracoes,
        'tempo_medio_ciclo': statistics.mean(tempos),
        'desvio_padrao': statistics.stdev(tempos) if len(tempos) > 1 else 0,
        'tempo_minimo': min(tempos),
        'tempo_maximo': max(tempos),
        'iteracoes': iteracoes,
        'tempos': tempos,
    }


def calcular_producao_esperada(maquinas, config, horas=8, dias=20):
    """Estimativa de produção mensal, considerando ciclos teóricos e reais."""
    minutos = horas * 60 * dias
    tc = calcular_tempo_ciclo(maquinas, config)
    if config == 'serie':
        pf, _ = calcular_prob_serie(maquinas)
    else:
        pf, _ = calcular_prob_paralelo(maquinas)

    ciclos = minutos / tc if tc > 0 else 0
    ciclos_ok = ciclos * (1 - pf)
    return {
        'ciclos_teoricos': ciclos,
        'ciclos_reais': ciclos_ok,
        'producao_esperada': int(ciclos_ok),
        'perda_producao': int(ciclos - ciclos_ok),
        'eficiencia': (ciclos_ok / ciclos * 100) if ciclos > 0 else 0,
    }
