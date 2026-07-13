"""
Tema visual (editorial dark) usado em todos os gráficos Plotly do dashboard.
"""

LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Space Grotesk', color='#555555', size=11),
    margin=dict(l=10, r=10, t=28, b=10),
)

LEGEND = dict(
    bgcolor='rgba(0,0,0,0)',
    font=dict(color='#888888', size=10, family='Space Mono'),
    bordercolor='#1f1f1f',
)

GRID = 'rgba(255,255,255,0.04)'

C = dict(
    blue='#0057FF', red='#FF2D2D', amber='#FFB800', green='#00C46A',
    gray='#555555', white='#ffffff',
)

PAL = [C['blue'], C['white'], C['amber'], C['red'], C['green'], '#8888ff']


def ax(fig, rows=1, cols=1):
    """Aplica o estilo padrão de eixos (grade, cor, fonte) a uma figura Plotly."""
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            try:
                fig.update_xaxes(
                    gridcolor=GRID, zeroline=False, linecolor='#1f1f1f',
                    tickfont=dict(color='#555555', size=10, family='Space Mono'),
                    row=r, col=c,
                )
                fig.update_yaxes(
                    gridcolor=GRID, zeroline=False, linecolor='#1f1f1f',
                    tickfont=dict(color='#555555', size=10, family='Space Mono'),
                    row=r, col=c,
                )
            except Exception:
                pass
    return fig
