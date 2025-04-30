import plotly.graph_objects as go
import plotly.express as px

from .colors import *

def plot_dxf_entities(df):
    fig = go.Figure()

    for i, row in df.iterrows():
        tipo = row.get("type")
        coords = row.get("coordinates")
        color_index = int(row.get("color", 7))  # Padrão 7 (branco)

        color = autocad_colors.get(color_index, "#888888")  # cinza fallback

        if not coords or not isinstance(coords, list):
            continue

        x = [p[0] for p in coords]
        y = [p[1] for p in coords]

        if tipo in ["LWPOLYLINE", "POLYLINE", "LINE"]:
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode="lines",
                line=dict(color=color, width=1),
                name=f"{tipo} ({color_index})",
                hoverinfo="name"
            ))
        elif tipo == "CIRCLE":
            cx, cy = row.get("center", (0, 0))
            r = row.get("radius", 0)
            fig.add_shape(
                type="circle",
                x0=cx - r, y0=cy - r,
                x1=cx + r, y1=cy + r,
                line=dict(color=color)
            )

    fig.update_layout(
        title="Visualização Vetorial (padrão AutoCAD)",
        xaxis_title="X",
        yaxis_title="Y",
        autosize=True,
        showlegend=False,
        height=600
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig
