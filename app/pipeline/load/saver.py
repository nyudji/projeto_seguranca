import pandas as pd
import json
import os

def save_to_json(data, filename="dados_processados.json"):
    """Salva os dados em um arquivo JSON."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tratado_dir = os.path.join(base_dir, '..', '..', 'dados', 'tratado', 'funcionarios_risco')
    filepath = os.path.join(tratado_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em {filepath}")

def save_to_csv(data_list, filename="dados_processados.csv"):
    """
    Salva uma lista de dicionários em um arquivo CSV.
    Esta função agora espera uma lista de dados já "achatados".
    """
    # Cria o DataFrame diretamente da lista
    df = pd.DataFrame(data_list)
    
    # Define o caminho do arquivo (sua lógica de caminho está correta)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tratado_dir = os.path.join(base_dir, '..', '..', 'dados', 'tratado', 'funcionarios_risco')
    
    # Cria o diretório se ele não existir
    os.makedirs(tratado_dir, exist_ok=True)
    
    # Constrói o caminho completo do arquivo
    filepath = os.path.join(tratado_dir, filename)
    
    # Salva no arquivo CSV
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Dados salvos em {filepath}")

def save_to_sql(data, connection_string, table_name="processos_funcionarios"):
    """Salva os dados em um banco de dados SQL."""
    # Lógica para conexão com o banco de dados (ex: SQLAlchemy)
    # Exemplo:
    # from sqlalchemy import create_engine
    # engine = create_engine(connection_string)
    #
    # flattened_data = ... # Use a mesma lógica do CSV para achatar
    # df = pd.DataFrame(flattened_data)
    #
    # df.to_sql(table_name, engine, if_exists='replace', index=False)
    # print(f"Dados salvos na tabela '{table_name}'")
    pass # Implemente a sua lógica aqui