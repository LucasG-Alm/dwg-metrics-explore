import subprocess

def convert_dwg_to_dxf(input_folder, output_folder):
    converter_path = r"C:\\Program Files\\ODA\\ODAFileConverter 25.12.0\\ODAFileConverter.exe"

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