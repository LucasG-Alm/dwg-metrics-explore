import os
import ezdxf
import pandas as pd

from .metrics import *
from .file_manager import *

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
def processar_arquivo(caminho, folder_origin, folder_output):
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

def extrair_dataframe_do_dxf(caminho_arquivo: str) -> pd.DataFrame:
    doc = ezdxf.readfile(caminho_arquivo)
    dados_entidades = []

    # Modelspace
    for entity in doc.modelspace():
        dados_entidades.append(extract_entity_data(entity, "Model Space"))

    # Layouts
    for layout in doc.layouts:
        for entity in layout:
            dados_entidades.append(extract_entity_data(entity, layout.name))

    return pd.DataFrame(dados_entidades)


def exportar_dataframe_para_excel(df: pd.DataFrame, caminho_destino: str):
    garantir_diretorio(caminho_destino)

    with pd.ExcelWriter(f'{caminho_destino}.xlsx', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Original', index=False)

        for tipo in df['type'].unique():
            aba = df[df['type'] == tipo].dropna(axis=1, how='all')
            aba.to_excel(writer, sheet_name=tipo[:31], index=False)  # Nome de aba limitado a 31 chars

# Função para extrair a tabela de layers com mais propriedades
def extrair_layers(caminho_arquivo: str):
    # Carrega o arquivo DXF
    doc = ezdxf.readfile(caminho_arquivo)
    
    # Acessa a tabela de layers
    layers = doc.layers

    # Extrai as informações sobre cada layer
    layer_info = []
    for layer in layers:
        layer_info.append({
            'Name': layer.dxf.name,
            'Color': layer.dxf.color,
            'Linetype': layer.dxf.linetype,  # Tipo de linha
            'Lineweight': layer.dxf.lineweight,  # Espessura
            'Status': 'Active' if layer.dxf.is_active else 'Inactive'
        })

    return layer_info
