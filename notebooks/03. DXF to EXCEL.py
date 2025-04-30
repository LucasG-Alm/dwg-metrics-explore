import json
from datetime import datetime
import numpy as np
import ezdxf
import pandas as pd
import os
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


arquivos = obter_informacoes_arquivos('database\\projects\\CESAN 2025')

df = arquivos
df = pd.DataFrame(df)
#filtro = ~df['caminho'].str.contains('OLD|NOTAS|Notas|ANTIGO|RECEBIDOS', regex=True)
#df = df[filtro]
#filtro = df['caminho'].str.contains('CAD|REDE|MAP|PREF', regex=True)
#filtro = df['caminho'].str.contains('Furo', regex=True)
#df = df[filtro]
df = df.reset_index().drop(columns=['index'])
df

# Converter a coluna para datetime (caso necessário)
df['data_criacao'] = pd.to_datetime(df['tempo_modificacao'], format='%d/%m/%Y %H:%M')

# Definir a data de corte
data_corte = pd.to_datetime('03/01/2025 00:00', format='%d/%m/%Y %H:%M')

# Filtrar para datas maiores que o corte
df = df[df['data_criacao'] > data_corte]
df = df.reset_index()
df = df.drop(columns=['index'])
df

import numpy as np

def calcular_comprimento_vetorial(coordenadas):
    # Converte a lista de coordenadas em um array numpy
    coords = np.array(coordenadas)
    
    # Calcula as diferenças entre pontos consecutivos
    diffs = np.diff(coords, axis=0)
    
    # Calcula a norma (distância euclidiana) de cada diferença e soma para obter o comprimento
    comprimento = np.sum(np.linalg.norm(diffs, axis=1))
    
    return comprimento


# Função para converter atributos para um formato serializável
def convert_to_serializable(value):
    if isinstance(value, (list, tuple)):
        return [convert_to_serializable(v) for v in value]
    elif isinstance(value, dict):
        return {k: convert_to_serializable(v) for k, v in value.items()}
    elif isinstance(value, (int, float, str, bool, type(None))):
        return value
    elif callable(value):
        return str(value)  # Converte funções e métodos para strings
    elif hasattr(value, '__dict__'):
        return convert_to_serializable(value.__dict__)
    else:
        return str(value)

# Função para extrair dados genéricos de qualquer entidade DXF
def extract_entity_data(entity):
    data = {'type': entity.dxftype()}
    for attr in dir(entity.dxf):
        if not attr.startswith('_'):
            try:
                data[attr] = getattr(entity.dxf, attr)
            except AttributeError:
                data[attr] = None
    return data

# Função para extrair dados genéricos de qualquer entidade DXF
def extract_entity_data(entity, space):
    data = {'type': entity.dxftype()}
    
    # Adiciona informações sobre o espaço (Model ou Layout)
    data['space'] = space

    # Adiciona verificação para salvar dados de blocos (INSERT)
    if entity.dxftype() == 'INSERT':
        data['block_name'] = entity.dxf.name  # Nome do bloco
        data['handle'] = entity.dxf.handle    # Handle do bloco
        data['insertion_point'] = (entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)  # Ponto de inserção
        data['rotation'] = entity.dxf.rotation  # Rotação
        data['xscale'] = entity.dxf.xscale  # Escala em X
        data['yscale'] = entity.dxf.yscale  # Escala em Y
        data['zscale'] = entity.dxf.zscale  # Escala em Z

        # Extrair atributos de blocos, se houver
        if hasattr(entity, 'attribs') and entity.attribs:
            data['attributes'] = {att.dxf.tag: att.dxf.text for att in entity.attribs}
    
    # Adiciona verificação para salvar coordenadas de polilinhas
    elif entity.dxftype() == 'LWPOLYLINE':
        data['coordinates'] = [(float(point[0]), float(point[1]), float(point[2])) for point in entity]
        data['is_closed'] = entity.closed  # Verifica se a polilinha é fechada
        data['length'] = calcular_comprimento_vetorial(data['coordinates'])
  
    elif entity.dxftype() == 'POLYLINE':
        data['coordinates'] = [(vertex.dxf.location.x, vertex.dxf.location.y,  vertex.dxf.location.z) for vertex in entity.vertices]
        data['is_closed'] = entity.is_closed  # Verifica se a polilinha é fechada
        data['length'] = calcular_comprimento_vetorial(data['coordinates']) # Comprimento da polilinha

    elif entity.dxftype() == 'LINE':
        start = entity.dxf.start
        end = entity.dxf.end
        data['coordinates'] = [(start.x, start.y, start.z), (end.x, end.y, end.z)]
        data['length'] = entity.dxf.start.distance(end)  # Comprimento da linha   
         
    # Arcos e Círculos
    elif entity.dxftype() in ['CIRCLE', 'ARC']:
        data['center'] = (entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z)
        data['radius'] = entity.dxf.radius
        if entity.dxftype() == 'ARC':
            data['start_angle'] = entity.dxf.start_angle
            data['end_angle'] = entity.dxf.end_angle
            
    # Extrai outros atributos
    for attr in dir(entity.dxf):
        if not attr.startswith('_'):
            try:
                value = getattr(entity.dxf, attr)
                data[attr] = convert_to_serializable(value)
            except AttributeError:
                data[attr] = None
    
    return data

# Função para salvar os dados em um DataFrame
def save_to_dataframe(dxf_file):
    doc = ezdxf.readfile(dxf_file)
    
    entities_data = []
    
    # Coletar dados de todas as entidades no Model Space
    for entity in doc.modelspace():
        entity_data = extract_entity_data(entity, 'Model Space')
        entities_data.append(entity_data)
    
    # Coletar dados de todas as entidades em cada Layout
    for layout in doc.layouts:
        for entity in layout:
            entity_data = extract_entity_data(entity, layout.name)  # Nome do Layout
            entities_data.append(entity_data)
    
    # Criar o DataFrame com os dados das entidades
    df = pd.DataFrame(entities_data)
    return df

import os
import pandas as pd
from tqdm import tqdm  # Importando corretamente

# Configurações de pastas
folder_origin = 'database\\projects'
folder_output = 'database\\projects data'

# Listas para metadados
data = {
    'arquivo': [],
    'categoria': [],
    'Lin': [],
    'Col': []
}

# Função para salvar metadados
def salvar_metadados(arquivo, categoria, df):
    data['arquivo'].append(arquivo)
    data['categoria'].append(categoria)
    data['Lin'].append(df.shape[0])
    data['Col'].append(df.shape[1])

# Função principal de processamento
def processar_arquivo(caminho):
    df = save_to_dataframe(caminho)
    caminho_relativo = os.path.relpath(caminho, folder_origin)
    caminho_destino = os.path.join(folder_output, caminho_relativo).replace('.dxf', '')

    # Cria as subpastas necessárias (apenas uma vez por arquivo)
    os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

    # Extrai o nome do arquivo
    arquivo = os.path.basename(caminho_destino)
    # Identificar colunas que contêm qualquer valor começando com "<" em todo o DataFrame
    #cols_to_drop = df.columns[(df.astype(str).apply(lambda x: x.str.startswith('<'))).any()]
    # Remover as colunas identificadas
    #df = df.drop(columns=cols_to_drop)
    caminho_destino = f'\\\\?\\{os.path.abspath(caminho_destino)}'


    #print(caminho_destino)
    #print(arquivo)

    # Cria o ExcelWriter e salva cada categoria em uma aba
    with pd.ExcelWriter(f'{caminho_destino}.xlsx', engine='xlsxwriter') as writer:
        salvar_metadados(arquivo, 'Original', df)  # Metadados do arquivo completo

        # Itera pelas categorias e salva em abas separadas
        for categoria in df['type'].unique():
            df_categoria = df[df['type'] == categoria].dropna(axis=1, how='all')
            salvar_metadados(arquivo, categoria, df_categoria)
            df_categoria.to_excel(writer, sheet_name=categoria, index=False)



    #print(f'Dados Extraídos de: {arquivo}')

# Inicializa o tqdm
with tqdm(total=len(df), desc='Processando arquivos', unit='arquivo') as pbar:
    for _, linha in df.iterrows():
        # Atualiza o tqdm com o nome do arquivo atual e tamanho
        pbar.set_postfix({
            "Arquivo Atual": os.path.basename(linha['caminho']),
            "Tamanho": linha['tamanho']
        })

        # Simula o processamento de cada arquivo
        processar_arquivo(linha['caminho'])
        # Aqui você incluiria a lógica de cópia ou outras ações
        pbar.update(1)  # Incrementa o progresso

# Criando DataFrame final com metadados
df_metadados = pd.DataFrame(data)
#display(df_metadados)

df_metadados.to_excel('database\\projects data\\CESAN 2025\\CESAN 2025.xlsx')

print(pd.io.excel._base.ExcelWriter.__doc__)


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
                #print(f"Erro ao deletar {caminho_completo}: {e}")
                e

# Exemplo de uso
diretorio = r"C:\\Users\\lucas.almeida\\OneDrive - sanejet\\PROGRMAÇÃO\\KMZ TO XLSX\\database\\projects data"  # Substituir pelo caminho desejado
deletar_pastas_vazias(diretorio)




