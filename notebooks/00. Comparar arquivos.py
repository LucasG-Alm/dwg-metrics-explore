import os
from datetime import datetime
import pandas as pd
from tqdm import tqdm

tqdm.pandas()

def obter_informacoes_arquivos(pasta):
    informacoes_arquivos = []

    for pasta_atual, sub_pastas, arquivos in tqdm(os.walk(pasta)):
        for arquivo in arquivos:
            caminho_completo = os.path.join(pasta_atual, arquivo)

            try:
                info = os.stat(caminho_completo)
            except (PermissionError, FileNotFoundError) as e:
                # Lidar com exceções (pular o arquivo e imprimir uma mensagem, se desejar)
                print(f"Erro ao obter informações de {caminho_completo}: {e}")
                continue

            # Extrair informações desejadas
            caminho_arquivo = caminho_completo
            arquivo, tipo_arquivo = os.path.splitext(arquivo)
            autor = info.st_uid
            data_criacao = datetime.fromtimestamp(info.st_ctime).strftime("%d/%m/%Y %H:%M")
            tempo_acesso = datetime.fromtimestamp(info.st_atime).strftime("%d/%m/%Y %H:%M")
            tempo_modificacao = datetime.fromtimestamp(info.st_mtime).strftime("%d/%m/%Y %H:%M")
            tempo_mudanca = datetime.fromtimestamp(info.st_ctime).strftime("%d/%m/%Y %H:%M")
            tamanho_arquivo = info.st_size

            # Criar um dicionário com as informações
            informacao_arquivo = {
                'caminho': caminho_arquivo,
                'arquivo': arquivo,
                'tipo_arquivo': tipo_arquivo,
                'data_criacao': data_criacao,
                'tempo_acesso': tempo_acesso,
                'tempo_modificacao': tempo_modificacao,
                'tempo_mudanca': tempo_mudanca,
                'tamanho': tamanho_arquivo
            }

            # Adicionar à lista de informações
            informacoes_arquivos.append(informacao_arquivo)
    print(informacoes_arquivos)
    return informacoes_arquivos


def arquivo_mais_recente(pasta, tipo_arquivo=None, data="tempo_acesso"):
    arquivos = obter_informacoes_arquivos(pasta)
    df_arquivos = pd.DataFrame(arquivos)

    # Filtrar por tipo de arquivo apenas se tipo_arquivo não for None
    if tipo_arquivo is not None:
        filtro = df_arquivos['tipo_arquivo'].str.contains(tipo_arquivo, regex=True)
        df_arquivos = df_arquivos[filtro]

    # Ordenar por data
    df_arquivos = df_arquivos.sort_values(by=data)

    arquivo = df_arquivos[0]

    return df_arquivos


# %%
registros = obter_informacoes_arquivos('database\\projects\\10002-CESAN') #arquivo_mais_recente('database\list files')
df_registros = pd.DataFrame(registros)
df_registros['data_criacao'].unique()

# %%



