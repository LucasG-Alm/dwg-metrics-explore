import numpy as np

def calcular_comprimento_vetorial(coordenadas):
    # Converte a lista de coordenadas em um array numpy
    coords = np.array(coordenadas)
    
    # Calcula as diferenças entre pontos consecutivos
    diffs = np.diff(coords, axis=0)
    
    # Calcula a norma (distância euclidiana) de cada diferença e soma para obter o comprimento
    comprimento = np.sum(np.linalg.norm(diffs, axis=1))
    
    return comprimento