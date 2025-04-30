import os
from datetime import datetime
import pandas as pd
import shutil
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

def copiar_arquivos_para_temp(df, column, input_base, tmp_folder):
    """Copia os arquivos DWG específicos para uma pasta temporária, mantendo a estrutura."""
    arquivos_copiados = []

    for dwg_file in df[column]:
        if os.path.isfile(dwg_file) and dwg_file.lower().endswith(".dwg"):
            caminho_relativo = os.path.relpath(dwg_file, input_base)
            caminho_temp = os.path.join(tmp_folder, caminho_relativo)

            # Cria subpastas necessárias
            os.makedirs(os.path.dirname(caminho_temp), exist_ok=True)

            # Copia o arquivo para a pasta temporária
            shutil.copy(dwg_file, caminho_temp)
            arquivos_copiados.append(caminho_temp)
        else:
            print(f"Arquivo não encontrado ou inválido: {dwg_file}")
    
    return arquivos_copiados

def listar_arquivos(folder):
    """Lista todos os arquivos DXF na pasta orária e suas subpastas."""
    arquivos = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".dxf"):
                arquivos.append(os.path.join(root, file))
    return arquivos

def mover_arquivos(folder_origin, folder_detiny):
    """Move os arquivos convertidos da pasta temp/dxf para a estrutura correta na pasta de saída."""
    arquivos = listar_arquivos(folder_origin)
    for caminho in arquivos:
        caminho_relativo = os.path.relpath(caminho, folder_origin)
        print(caminho_relativo)
        caminho_destino = os.path.join(folder_detiny, caminho_relativo)
        print(caminho_destino)

        # Cria as subpastas necessárias no caminho de destino, caso não existam
        os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

        # Substitui o arquivo antigo pelo novo no local de destino
        if os.path.exists(caminho_destino):
            os.remove(caminho_destino)  # Remove o antigo para evitar erro de substituição
        shutil.move(caminho, caminho_destino)  # Move o novo arquivo

        print(f"Arquivo {caminho} movido para {caminho_destino}")

def remover_pasta_temp(tmp_folder):
    """Remove a pasta temporária e seus conteúdos."""
    shutil.rmtree(tmp_folder, ignore_errors=True)
    print("Pasta temporária removida.")

def deletar_pastas_vazias(diretorio_raiz):
    # Percorre a estrutura de diretórios de baixo para cima (bottom-up)
    for root, dirs, files in os.walk(diretorio_raiz, topdown=False):
        for dir_name in dirs:
            caminho_completo = os.path.join(root, dir_name)

            # Tenta remover a pasta, se estiver vazia
            try:
                os.rmdir(caminho_completo)
                print(f"Pasta vazia deletada: {caminho_completo}")
            except OSError as e:
                # Se não puder deletar, provavelmente não está vazia
                print(f"Erro ao deletar {caminho_completo}: {e}")

def garantir_diretorio(caminho_completo: str):
    pasta = os.path.dirname(caminho_completo)
    if not os.path.exists(pasta):
        os.makedirs(pasta)