def apply_dark(fig, is_heatmap=False):
    """Terapkan tema gelap ke figure Plotly."""
    fig.update_layout(
        plot_bgcolor='#1c2128',
        paper_bgcolor='#161b22',
        font=dict(family='IBM Plex Sans', color='#e6edf3', size=13),
        title_font=dict(size=15, color='#e6edf3'),
        legend=dict(bgcolor='#1c2128', bordercolor='#30363d',
                    borderwidth=1, font=dict(color='#e6edf3')),
        margin=dict(t=50, b=50, l=55, r=30),
        autosize=True,
    )
    if not is_heatmap:
        ax = dict(
            gridcolor='#30363d',
            zerolinecolor='#30363d',
            linecolor='#30363d',
            tickfont=dict(color='#8b949e'),
            title_font=dict(color='#e6edf3')
        )
        fig.update_xaxes(**ax)
        fig.update_yaxes(**ax)