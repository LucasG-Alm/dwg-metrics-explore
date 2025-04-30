import streamlit as st
import pandas as pd
import os

from src.utils.extractor_dxf import extrair_dataframe_do_dxf, exportar_dataframe_para_excel
from src.utils.converter import convert_dwg_to_dxf
from src.visual import plot_dxf_entities

# Pastas do sistema
TMP_DWG = 'tmp/dwg'
TMP_DXF = 'tmp/dxf'
OUTPUT = 'tmp/excel'

# Criar diretórios
os.makedirs(TMP_DWG, exist_ok=True)
os.makedirs(TMP_DXF, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

# Configuração da interface
st.set_page_config(page_title="DWG Metrics Explorer", layout="wide")
st.title("📐 DWG Metrics Explorer")
st.sidebar.header("Upload e Filtros")

# Upload de arquivos
uploaded_files = st.sidebar.file_uploader(
    "Enviar arquivos .DWG ou .DXF",
    type=["dwg", "dxf"],
    accept_multiple_files=True
)

# Se arquivos forem enviados
if uploaded_files:
    arquivos_dwg = []
    arquivos_dxf = []

    for file in uploaded_files:
        ext = os.path.splitext(file.name)[-1].lower()
        destino = TMP_DWG if ext == '.dwg' else TMP_DXF
        caminho = os.path.join(destino, file.name)

        with open(caminho, "wb") as f:
            f.write(file.read())

        if ext == '.dwg':
            arquivos_dwg.append(caminho)
        elif ext == '.dxf':
            arquivos_dxf.append(caminho)

    st.sidebar.success(f"✅ {len(uploaded_files)} arquivos salvos!")

    # 2. Converter apenas os DWGs (se houver)
    if arquivos_dwg and "conversao_realizada" not in st.session_state:
        with st.spinner("🔄 Convertendo DWGs para DXF..."):
            convert_dwg_to_dxf(TMP_DWG, TMP_DXF)
            st.session_state.conversao_realizada = True
            st.success("✅ Conversão concluída!")

    # 3. Listar DXFs disponíveis para análise
    dxf_files = [
        f for f in os.listdir(TMP_DXF)
        if f.lower().endswith(".dxf")
    ]

    # 4. Selecionar um para pré-visualizar
    arquivo_selecionado = st.selectbox("👁️ Escolha um arquivo para visualizar", dxf_files)

    if arquivo_selecionado:
        caminho_dxf = os.path.join(TMP_DXF, arquivo_selecionado)

        # 5. Extrair dados
        with st.spinner(f"📥 Extraindo dados de `{arquivo_selecionado}`..."):
            df = extrair_dataframe_do_dxf(caminho_dxf)
            # Identificar colunas que contêm qualquer valor começando com "<" em todo o DataFrame
            cols_to_drop = df.columns[(df.astype(str).apply(lambda x: x.str.startswith('<'))).any()]
            # Remover as colunas identificadas
            df = df.drop(columns=cols_to_drop)

        # 6. Visualização e filtros
        st.subheader("📊 Prévia dos dados extraídos")
        st.dataframe(df.head(100))
        
        tipos = df["type"].unique()
        filtro_tipo = st.multiselect("Filtrar por tipo de entidade:", tipos, default=list(tipos))

        df_filtrado = df[df["type"].isin(filtro_tipo)]
        st.write(f"🔎 {len(df_filtrado)} entidades após o filtro.")
        st.dataframe(df_filtrado)

        # 7. Visualização vetorial
        st.subheader("🧭 Visualização vetorial")
        coluna_cor = st.selectbox("Colorir por:", options=["layer", "type"], index=0)
        fig = plot_dxf_entities(df_filtrado, color_by=coluna_cor)
        st.plotly_chart(fig, use_container_width=True)


        # 7. Exportação
        if st.button("💾 Exportar para Excel"):
            nome_base = os.path.splitext(arquivo_selecionado)[0]
            caminho_exportacao = os.path.join(OUTPUT, nome_base)
            exportar_dataframe_para_excel(df_filtrado, caminho_exportacao)
            st.success(f"📁 Arquivo salvo em `{caminho_exportacao}.xlsx`")
else:
    st.info("Envie arquivos DWG pelo menu lateral para iniciar.")

if st.sidebar.button("🔁 Resetar sessão"):
    st.session_state.clear()
    st.experimental_rerun()

