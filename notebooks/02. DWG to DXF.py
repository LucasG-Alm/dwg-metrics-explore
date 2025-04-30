
import os
from datetime import datetime
import pandas as pd
import shutil
import subprocess

df = pd.read_excel('tmp/projetos_origem.xlsx')
df = df[df['tipo_arquivo']=='.dwg']
filtro = ~df['caminho'].str.contains('OLD|NOTAS|Notas|ANTIGOS|Antigos', regex=True)
df = df[filtro]
#filtro = df['caminho'].str.contains('CAD|REDE|MAP|PREF|TOP|BUILT', regex=True)
#filtro = df['caminho'].str.contains('Furo', regex=True)
df = df[filtro]
df = df.reset_index().drop(columns=['index'])
df

# Converter a coluna para datetime (caso necessário)
df['tempo_modificacao'] = pd.to_datetime(df['tempo_modificacao'], format='%d/%m/%Y %H:%M')

# Definir a data de corte
data_corte = pd.to_datetime('03/01/2024 00:00', format='%d/%m/%Y %H:%M')

# Filtrar para datas maiores que o corte
df = df[df['tempo_modificacao'] > data_corte]
df

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

def convert_dwg_to_dxf(input_folder, output_folder):
    converter_path = r"C:\\Program Files\\ODA\\ODAFileConverter 25.8.0\\ODAFileConverter.exe"

    command = [
        converter_path,
        input_folder,
        output_folder,
        "ACAD2018",  # Versão de saída
        "DXF",  # Tipo de saída
        "1",  # Auditar cada arquivo
        "1"  # Recursivo (subpastas)
    ]

    try:
        print(f"Executando: {' '.join(command)}")
        subprocess.run(command, shell=True, check=True)
        print("Conversão concluída com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a conversão: {e}")

# Exemplo de uso
#convert_dwg_to_dxf(
#    r"C:\\Users\\lucas.almeida\\OneDrive - Sanit\\CESAN\\PROJETOS\\02. VITÓRIA\\01. LEITÃO DA SILVA",
#    r"C:\\Users\\lucas.almeida\\OneDrive - sanejet\\PROGRMAÇÃO\\KMZ TO XLSX\\database\\projects"
#)


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

tmp_folder_input = "tmp\\dwg"
tmp_folder_output = "tmp\\dxf"
os.makedirs(tmp_folder_input, exist_ok=True)
os.makedirs(tmp_folder_output, exist_ok=True)

folder_input = 'C:\\Users\\lucas.almeida\\OneDrive - Sanit\\10002 - CENSAN PLANEJAMENTO\\PROJETOS'
arquivos_copiados = copiar_arquivos_para_temp(df, 'caminho', folder_input, tmp_folder_input)

convert_dwg_to_dxf(tmp_folder_input, tmp_folder_output)

folder_output = 'database\\projects\\CESAN 2025'
mover_arquivos(tmp_folder_output, folder_output)

shutil.rmtree(tmp_folder_input, ignore_errors=True)
shutil.rmtree(tmp_folder_output, ignore_errors=True)

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

# Exemplo de uso
diretorio = r"C:\\Users\\lucas.almeida\\OneDrive - sanejet\\PROGRMAÇÃO\\KMZ TO XLSX\\database\\projects"  # Substituir pelo caminho desejado
deletar_pastas_vazias(diretorio)






