# 📐 DWG Metrics Explorer

O DWG Metrics Explorer é uma aplicação web desenvolvida em Python que permite analisar e extrair métricas de arquivos DWG (AutoCAD). A aplicação converte arquivos DWG para DXF e extrai informações detalhadas sobre as entidades presentes nos desenhos.

## �� Funcionalidades

- **Upload de Arquivos**
  - Suporte a múltiplos arquivos DWG
  - Interface drag-and-drop para upload
  - Validação de formato de arquivo

- **Conversão e Processamento**
  - Conversão automática de DWG para DXF
  - Processamento em lote de múltiplos arquivos
  - Gerenciamento automático de arquivos temporários

- **Análise de Dados**
  - Extração de métricas detalhadas das entidades
  - Filtragem por camadas (layers)
  - Filtragem por tipos de entidades (linhas, círculos, blocos, etc.)
  - Visualização de estatísticas básicas

- **Exportação**
  - Exportação dos dados para Excel
  - Formatação automática das planilhas
  - Organização dos dados por camadas e tipos de entidades

## 📁 Estrutura do Projeto

```
DWG Metrics Explorer/
├── app.py                  # Aplicação principal Streamlit
├── data/                   # Diretório para dados
├── tmp/                    # Diretório temporário para conversão
│   ├── dwg/                # Arquivos DWG temporários
│   └── dxf/                # Arquivos DXF convertidos
│   └── output/             # Diretório para arquivos exportados
├── src/                    # Código fonte
│   └── utils/              # Utilitários
├── tests/                  # Testes unitários e de integração
├── notebooks/              # Jupyter notebooks para análise
├── assets/                 # Recursos visuais
├── .venv/                  # Ambiente virtual
├── pyproject.toml          # Configuração do Poetry
├── poetry.lock             # Dependências travadas
└── requirements.txt        # Dependências do projeto
```

## 🛠️ Tecnologias Utilizadas

- **Backend**
  - Python 3.x
  - Streamlit (interface web)
  - Pandas (processamento de dados)
  - ezdxf (manipulação de arquivos DXF)
  - Poetry (gerenciamento de dependências)

- **Frontend**
  - Streamlit UI
  - Plotly (visualizações)
  - Pandas DataFrame (tabelas interativas)

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Poetry 1.4.0 ou superior
- Sistema operacional Windows (para compatibilidade com arquivos DWG)
- Espaço em disco suficiente para processamento de arquivos temporários

## 🚀 Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/dwg-metrics-explorer.git
   cd dwg-metrics-explorer
   ```

2. Instale as dependências:
   ```bash
   poetry install
   ```

3. Ative o ambiente virtual:
   ```bash
   poetry shell
   ```

4. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

5. Acesse a aplicação no navegador:
   ```
   http://localhost:8501
   ```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

