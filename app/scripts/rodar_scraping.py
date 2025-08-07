import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import TJSP_Scraper

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    """Função principal que orquestra a execução do scraper."""
    logging.info("Iniciando a aplicação de scraper do TJSP.")
    cpf = input("Digite o CPF/CNPJ: ").strip()
    nome = input("Digite o nome completo: ").strip()

    try:
        scraper_tjsp = TJSP_Scraper(cpf_cnpj=cpf, nome_completo=nome)
        await scraper_tjsp.run()
    except Exception as e:
        logging.error(f"Ocorreu um erro na execução principal: {e}")

if __name__ == "__main__":
    asyncio.run(main())