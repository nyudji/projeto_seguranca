from datetime import datetime
import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import TJSP_Scraper
from pipeline.load.saver import save_to_json, save_to_csv, save_to_sql

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():

    def converter_para_formato_csv(data):
        """Converte os dados extraídos para um formato adequado para CSV.
        """
        registros = []
        nome_funcionario = data.get("funcionario", {}).get("nome", "")
        cpf_cnpj_funcionario = data.get("funcionario", {}).get("cpf", "")
        processos = data.get("processos", [])
        
        for processo in processos:
            registro = {
                "funcionario_nome": nome_funcionario,
                "funcionario_cpf_cnpj": cpf_cnpj_funcionario,
                "risco": processo.get("risco"),
                "fonte": processo.get("fonte"),
                "descricao": processo.get("descricao")
            }
            if "numero_processo" in processo:
                registro["numero_processo"] = processo["numero_processo"]
            if "grau" in processo:
                registro["grau"] = processo["grau"]
            registros.append(registro)
            
        return registros

    """Função principal que orquestra a execução do scraper."""
    logging.info("Iniciando a aplicação de scraper do TJSP.")

    funcionarios = [
        {"nome": "João Pereira Amaral de Souza", "cpf": "567.3435.234-03"},
        {"nome": "Maria Carvalho Pereira de Souza", "cpf": "425.656.323-03"}
    ]
    #cpf = input("Digite o CPF/CNPJ: ").strip()
    #nome = input("Digite o nome completo: ").strip()
    
    todos_os_registros = []
    try:
        for funcionario in funcionarios:
            logging.info(f"Iniciando consulta para {funcionario['nome']}...")
            
            # Extração e Processamento para um funcionário
            scraper = TJSP_Scraper(funcionario["cpf"], funcionario["nome"])
            resultado_completo = await scraper.run()
            
            # Obtém a data atual no formato 'MM_AAAA'
            data_atual = datetime.now().strftime('%d_%m_%Y')

            # Obter os 4 primeiros dígitos do CPF e remover caracteres
            cpf_limpo = funcionario['cpf'].replace('.', '').replace('-', '')
            cpf_prefixo = cpf_limpo[:4]

            # Formatar o nome do funcionário
            nome_base = funcionario['nome'].replace(' ', '_')

            # Construir o nome do arquivo no formato 'nome_cpf_data.json'
            filename_json = f"{nome_base}-{cpf_prefixo}_{data_atual}.json"

            # Salva o registro completo em JSON (por funcionário)
            save_to_json(resultado_completo, filename_json)

            # Converte os dados para o formato CSV e adiciona à lista geral
            registros_csv = converter_para_formato_csv(resultado_completo)
            logging.info(f"Registros convertidos para {funcionario['nome']}: {registros_csv}")
            todos_os_registros.extend(registros_csv)


        # Salva o arquivo CSV consolidado com todos os funcionários
        logging.info(f"Total de registros para o CSV: {len(todos_os_registros)}")
        if todos_os_registros:
            save_to_csv(todos_os_registros, "todos_riscos.csv")
        else:
            logging.warning("Nenhum registro encontrado para salvar no CSV.")
        
    except Exception as e:
        logging.error(f"Ocorreu um erro na execução principal: {e}")


if __name__ == "__main__":
    asyncio.run(main())