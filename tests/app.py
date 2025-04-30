import streamlit as st
import ezdxf
import pandas as pd
import tempfile
import os

# --- Configurações básicas
st.set_page_config(page_title="DWG Metrics Explorer", layout="wide")
st.title("DWG Metrics Explorer 🚀")

# --- Sidebar
st.sidebar.header("⚙️ Configurações")
uploaded_file = st.sidebar.file_uploader("Upload do arquivo DXF", type=["dxf"])

if uploaded_file is not None:
    # Salva o arquivo temporariamente
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    # --- Leitura do DXF
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    st.sidebar.success("Arquivo carregado!")

    # --- Extrair entidades básicas
    entidades = []
    for e in msp:
        if e.dxftype() in ["LINE", "LWPOLYLINE", "POLYLINE"]:
            entidade_info = {
                "Tipo": e.dxftype(),
                "Layer": e.dxf.layer,
                "Comprimento": e.length() if hasattr(e, "length") else None,
                "Cor": e.dxf.color,
            }
            entidades.append(entidade_info)

    df = pd.DataFrame(entidades)

    # --- Filtros
    st.sidebar.subheader("🔎 Filtros")

    layers = df["Layer"].unique()
    selected_layers = st.sidebar.multiselect("Selecionar Layer(s)", layers, default=list(layers))

    tipos = df["Tipo"].unique()
    selected_types = st.sidebar.multiselect("Selecionar Tipo(s)", tipos, default=list(tipos))

    # --- Aplicar Filtro
    df_filtrado = df[
        (df["Layer"].isin(selected_layers)) &
        (df["Tipo"].isin(selected_types))
    ]

    # --- Área principal
    st.subheader("📋 Entidades Filtradas")
    st.dataframe(df_filtrado)

    # --- Métricas
    st.subheader("📈 Métricas")
    st.metric(label="Total de Entidades", value=len(df_filtrado))
    st.metric(label="Soma dos Comprimentos", value=round(df_filtrado["Comprimento"].sum(), 2))

    # --- Exportação
    st.subheader("⬇️ Exportar")
    if st.button("Exportar para Excel"):
        output = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        df_filtrado.to_excel(output.name, index=False)
        with open(output.name, "rb") as file:
            st.download_button(label="Baixar Excel", data=file, file_name="metricas_filtradas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
