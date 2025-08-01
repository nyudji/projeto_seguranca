from playwright.sync_api import sync_playwright
import time
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def consultar_processos(cpf_cnpj: str, nome_completo: str) -> None:
    try:
        with sync_playwright() as p:
            #Variáveis de configuração
            URL = "https://esaj.tjsp.jus.br/esaj/portal.do?servico=190090"
            FORO = "São Paulo"
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            logging.info("Iniciando consulta de processos no TJSP")
            try:
                #Funcao preencher seções
                def preencher_secoes():
                    # Tenta preencher o campo de "Foro"
                    # Tenta preencher o campo de "Foro" (1º grau)
                    link_foros = page.get_by_role("link", name="Todos os foros")
                    if link_foros.is_visible():
                        link_foros.click()
                        page.get_by_role('combobox', name='Foro').fill(FORO[:7])
                        page.get_by_role('option', name=FORO, exact=True).locator('span').click()
                        return
                    else:
                        # Se o campo de "Foro" não estiver visível, tenta preencher o campo de "Seções
                        page.get_by_role("link", name="Todas as seções").click()
                        page.get_by_role("option", name="Todas as seções").click()
                        return
            except Exception as e:
                logging.error(f"Nenhum link de foro ou seção foi encontrado na página.: {e}")

            # Função para consultar processos   
            def consultar(tipo, campo, valor, msg_sem_processo, grau) -> bool:
                page.goto(URL)
                page.get_by_role("cell", name=f"Consulta de Processos do {grau}ºGrau Consulta de Processos do {grau}ºGrau").get_by_role("link").click()
                page.get_by_label("Consultar por").select_option(tipo)
                page.locator(campo).fill(valor)
                preencher_secoes()
                page.get_by_role('button', name='Consultar').click()
                mensagem = page.locator(f"text={msg_sem_processo}")
                time.sleep(0.8)
                try:
                    mensagem.wait_for(timeout=4000)
                    logging.info('Não encontrado processos')
                    time.sleep(0.8)
                    return False  # mensagem de "não encontrado" apareceu
                except:
                    return True
                finally:
                    time.sleep(0.8)
            # Realizando consultas
            # 1º grau
            try:
                if consultar("DOCPARTE", "#campo_DOCPARTE", cpf_cnpj, "Não existem informações",1):
                    logging.info(f'Processos encontrados para o CPF/CNPJ: {cpf_cnpj}')
                elif consultar("NMPARTE", "#campo_NMPARTE", nome_completo, "Não existem informações disponíveis para os parâmetros informados.",1):
                    logging.info(f'Processos encontrados para o nome: {nome_completo} - 1º grau')
                else:
                    logging.info('Nenhum processo localizado para o CPF/CNPJ ou nome informado. - 1º grau')
            except Exception as e:
                logging.error(f'❌ Erro durante a consulta processos 1 grau: {e}')
            # 2º grau
            try:
                page.goto(URL)
                if consultar("DOCPARTE", "#campo_DOCPARTE", cpf_cnpj, "Não existem informações",2):
                    logging.info(f'Processos encontrados para o CPF/CNPJ: {cpf_cnpj} - 2º grau')
                elif consultar("NMPARTE", "#campo_NMPARTE", nome_completo, "Não existem informações disponíveis para os parâmetros informados.",2):
                    logging.info(f'Processos encontrados para o nome: {nome_completo} - 2º grau')
                else:
                    logging.info('Nenhum processo localizado para o CPF/CNPJ ou nome informado. - 2º grau')
            except Exception as e:
                logging.error(f'❌ Erro durante a consulta processos 2 grau: {e}')
    except Exception as e:
        logging.error(f'Erro ao consultar processos no TJSP {e}')
    finally:
        browser.close()
        logging.info("Consulta finalizada e usuário sem registros de processos encontrados.")

if __name__ == "__main__":
    cpf = input("Digite o CPF/CNPJ: ").strip()
    nome = input("Digite o nome completo: ").strip()
    consultar_processos(cpf, nome)
