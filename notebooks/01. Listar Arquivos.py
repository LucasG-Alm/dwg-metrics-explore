import os
from datetime import datetime
import pandas as pd
from tqdm import tqdm

tqdm.pandas()
import re

def categoria_proj(nome_arquivo):
    # Define os padrões e as categorias correspondentes
    categorias = {
        "REDE": r"\bREDE\b",
        "PREF": r"\bPREF\b",
        "MAP": r"\bMAP\b",
        "TOP": r"\bTOP\b",
        "CAD": r"\bCAD\b",
        "SPT": r"\bSPT\b",
        "CAD": r"\bAS BILT\b",
        "CAD": r"\bAS BUILT\b",
        "RAMAL": r"\bRAMAL\b",
        "PLANO DE FURO": r"\bPF\b"
    }
    
    # Verifica qual padrão corresponde ao nome do arquivo
    for categoria, padrao in categorias.items():
        if re.search(padrao, nome_arquivo):
            return categoria
    
    # Retorna "Não definido" caso não encontre uma categoria
    return "Não definido"

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
            tamanho_arquivo = info.st_size,
            tipo_proj = categoria_proj(arquivo)

            # Criar um dicionário com as informações
            informacao_arquivo = {
                'caminho': caminho_arquivo,
                'arquivo': arquivo,
                'tipo_arquivo': tipo_arquivo,
                'tipo_proj': tipo_proj,
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

def criar_pasta_do_dia(df, caminho_base, nome):
    # Obtém a data atual
    data_atual = datetime.now()

    # Formata a data como YYYYMMDD
    data = data_atual.strftime("%Y-%m-%d")
    data_hora = data_atual.strftime("%Y-%m-%d_%H.%M.%S")

    # Constrói o caminho da pasta do dia
    caminho_pasta_do_dia = os.path.join(caminho_base, data)

    # Cria a pasta se ela não existir
    if not os.path.exists(caminho_pasta_do_dia):
        os.makedirs(caminho_pasta_do_dia)

    # Constrói o nome do arquivo com a data
    nome_arquivo = f'{caminho_pasta_do_dia}\{data_hora} - {nome}.csv'

    # Salva o DataFrame no arquivo
    df.to_csv(nome_arquivo)

    return df.to_csv(nome_arquivo)

caminho = ['C:\\Users\\lucas.almeida\\OneDrive - Sanit\\10002 - CENSAN PLANEJAMENTO\\PROJETOS', "P:\\PROJETOS"]
nome = ['CESAN 2025', 'CESAN 2025 BACKUP']

Pastas = {
  'nome': nome,
  'caminho': caminho
}

Pastas_df = pd.DataFrame(Pastas)

for index, row in tqdm(Pastas_df.iterrows()):

  informacoes = obter_informacoes_arquivos(row['caminho'])

  informacoes_df = pd.DataFrame(informacoes)
  informacoes_df['tamanho'] = informacoes_df['tamanho'].apply(lambda x: x[0] if isinstance(x, tuple) else x)
  informacoes_df['tamanho_kb'] = round(informacoes_df['tamanho']/1024, 2)

  #display(informacoes_df)

  informacoes_df = informacoes_df.sort_values(by='tipo_arquivo')
  print(informacoes_df['tipo_arquivo'].unique())

  nome = row['nome']
  caminho_pasta_do_dia = criar_pasta_do_dia(informacoes_df, '.\database\list files', nome)

df = informacoes_df
df
df.to_excel('tmp/projetos_origem.xlsx', index=False)

import os
import pandas as pd
import shutil
from tqdm import tqdm

def copiar_diferenca_csvs(csv_todos, csv_ja_copiados, extensoes_permitidas, pasta_destino, pasta_base):
    # Carrega os dois CSVs
    df_todos = pd.read_csv(csv_todos)
    df_ja_copiados = pd.read_csv(csv_ja_copiados)

    # Normaliza extensões e filtra os arquivos com extensões permitidas
    extensoes_permitidas = [ext.lower() for ext in extensoes_permitidas]
    #df_todos = df_todos[df_todos['tipo_arquivo'].str.lower().isin(extensoes_permitidas)]
    
    # Encontra a diferença entre os arquivos
    df_diferenca = pd.merge(
        df_todos,
        df_ja_copiados,
        on='caminho',
        how='left',
        indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    # Ordena por caminho e tamanho_kb_x
    df_diferenca = df_diferenca.sort_values(by=['tamanho_kb_x', 'caminho'], ascending=[True, True]).reset_index()
    df_diferenca = df_diferenca[4004:]
    #display(df_diferenca)

    # Inicializa o progresso com tqdm
    with tqdm(total=len(df_diferenca), desc="Copiando arquivos", unit="arquivo") as pbar:
        for _, linha in df_diferenca.iterrows():
            caminho_origem = linha['caminho']
            tamanho_kb_x = linha['tamanho_kb_x']

            # Atualiza o tqdm com o nome do arquivo atual e tamanho
            pbar.set_postfix({"Arquivo Atual": os.path.basename(caminho_origem), "Tamanho (KB)": tamanho_kb_x})

            # Extrai o caminho relativo após "PROJETOS"
            if pasta_base in caminho_origem:
                caminho_relativo = caminho_origem.split(pasta_base, 1)[-1].lstrip("\\/")
                caminho_destino = os.path.join(pasta_destino, caminho_relativo)

                # Cria os diretórios necessários na pasta de destino
                os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

                try:
                    # Copia o arquivo
                    shutil.copy2(caminho_origem, caminho_destino)
                    pbar.update(1)  # Atualiza o progresso
                except Exception as e:
                    print(f"Erro ao copiar o arquivo {caminho_origem}: {e}")
                    pbar.update(1)  # Ainda assim, atualiza o progresso


# Configurações
csv_todos = r"database\list files\2025-01-22\2025-01-22_23.12.40 - CESAN 2025 BACKUP.csv"
csv_ja_copiados = r"database\list files\2025-01-27\2025-01-27_00.13.26 - CESAN 2025.csv"
extensoes_permitidas = ['.dwg', '.pdf', '.xlsx', '.xlsm', '.png', '.jpg', '.kml', '.kmz', '.txt', '.jxl']
pasta_destino = r"P:\PROJETOS"
pasta_base = "PROJETOS"  # Define o ponto base para a estrutura

# Executa a cópia
copiar_diferenca_csvs(csv_todos, csv_ja_copiados, extensoes_permitidas, pasta_destino, pasta_base)



