# %%
import os
from datetime import datetime
import pandas as pd
from tqdm import tqdm

tqdm.pandas()

# %%
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
        "AS BUILT": r"\bAS BUILT\b",
        "RAMAL": r"\bRAMAL\b",
        "PLANO DE FURO": r"\bPF\b"
    }
    
    # Verifica qual padrão corresponde ao nome do arquivo
    for categoria, padrao in categorias.items():
        if re.search(padrao, nome_arquivo):
            return categoria
    
    # Retorna "Não definido" caso não encontre uma categoria
    return "Não definido"

# %%
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


# %%
def criar_pasta_do_dia(caminho_base, nome):
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
    informacoes_df.to_csv(nome_arquivo, encoding="utf-8")

    return informacoes_df.to_csv(nome_arquivo, encoding="utf-8")

# %%
caminho = ['database\\projects data', 'database\\projects\\10002-CESAN-25']
nome = ['Projects Data', 'Projects 10002-CENSAN 25']

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
  caminho_pasta_do_dia = criar_pasta_do_dia('.\\database\\list data', nome)


# %%
df = informacoes_df
df[['caminho', 'arquivo']]

# %%
df.to_excel('tmp/projetos_origem.xlsx', index=False)

# %%



