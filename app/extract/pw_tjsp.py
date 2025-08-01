import asyncio
import logging
from playwright.async_api import async_playwright

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def consultar_processos(cpf_cnpj: str, nome_completo: str) -> None:
    '''Função para consultar processos no TJSP usando Playwright.'''
    try:
        async with async_playwright() as p:
            
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            logging.info("Iniciando consulta de processos no TJSP")

            async def preencher_secoes():
                '''Função para preencher as seções ou foros na página de consulta.'''
                FORO = "Todos os foros"
                try:
                    link_foros = page.get_by_role("link", name="Todos os foros")
                    if await link_foros.is_visible():
                        await link_foros.click()
                        await page.get_by_role('combobox', name='Foro').fill(FORO[:7])
                        await page.get_by_role('option', name=FORO, exact=True).locator('span').click()
                    else:
                        await page.get_by_role("link", name="Todas as seções").click()
                        await page.get_by_role("option", name="Todas as seções").click()
                except Exception as e:
                    logging.error(f"Nenhum link de foro ou seção foi encontrado: {e}")

            async def consultar_instancia(tipo, campo, valor, msg_sem_processo, grau) -> bool:
                URL = "https://esaj.tjsp.jus.br/esaj/portal.do?servico=190090"
                await page.goto(URL)
                await page.get_by_role("cell", name=f"Consulta de Processos do {grau}ºGrau Consulta de Processos do {grau}ºGrau").get_by_role("link").click()
                await page.get_by_label("Consultar por").select_option(tipo)
                await page.locator(campo).fill(valor)
                await preencher_secoes()
                await page.get_by_role('button', name='Consultar').click()
                mensagem = page.locator(f"text={msg_sem_processo}")
                await asyncio.sleep(0.8)
                try:
                    await mensagem.wait_for(timeout=4000)
                    logging.info('Não encontrado processos')
                    await asyncio.sleep(0.8)
                    return False
                except:
                    return True
                finally:
                    await asyncio.sleep(0.8)

            async def cosultar_requisitorios(tipo, campo, valor, msg_sem_processo) -> bool:
                URL = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do"
                await page.goto(URL)
                await page.get_by_label("Consultar por").select_option(tipo)
                await page.locator(campo).fill(valor)
                await page.get_by_role('button', name='Consultar').click()
                mensagem = page.locator(f"text={msg_sem_processo}")
                await asyncio.sleep(0.8)
                try:
                    await mensagem.wait_for(timeout=4000)
                    logging.info('Não encontrado requisitórios')
                    await asyncio.sleep(0.8)
                    return False
                except:
                    return True
                finally:
                    await asyncio.sleep(0.8)

            # 1º grau
            try:
                if await consultar_instancia("DOCPARTE", "#campo_DOCPARTE", cpf_cnpj, "Não existem informações", 1):
                    logging.info(f'Processos encontrados para o CPF/CNPJ: {cpf_cnpj}')
                elif await consultar_instancia("NMPARTE", "#campo_NMPARTE", nome_completo, "Não existem informações disponíveis para os parâmetros informados.", 1):
                    logging.info(f'Processos encontrados para o nome: {nome_completo} - 1º grau')
                else:
                    logging.info('Nenhum processo localizado - 1º grau')
            except Exception as e:
                logging.error(f'❌ Erro durante a consulta processos 1º grau: {e}')

            # 2º grau
            try:
                if await consultar_instancia("DOCPARTE", "#campo_DOCPARTE", cpf_cnpj, "Não existem informações", 2):
                    logging.info(f'Processos encontrados para o CPF/CNPJ: {cpf_cnpj} - 2º grau')
                elif await consultar_instancia("NMPARTE", "#campo_NMPARTE", nome_completo, "Não existem informações disponíveis para os parâmetros informados.", 2):
                    logging.info(f'Processos encontrados para o nome: {nome_completo} - 2º grau')
                else:
                    logging.info('Nenhum processo localizado - 2º grau')
            except Exception as e:
                logging.error(f'❌ Erro durante a consulta processos 2º grau: {e}')

            # Consulta de requisitórios
            logging.info("Iniciando consulta de requisitórios")
            await asyncio.sleep(0.8)
            try:
                if await cosultar_requisitorios("DOCPARTE", "#campo_DOCPARTE", cpf_cnpj, "Não existem informações disponíveis para os parâmetros informados."):
                    logging.info(f'Requisitorios encontrados para o CPF/CNPJ: {cpf_cnpj} - Repositórios')
            except Exception as e:
                logging.error(f'❌ Erro durante a consulta de requisitórios: {e}')      

            # Fechando o navegador
            await browser.close()
            logging.info("Consulta finalizada.")

    except Exception as e:
        logging.error(f'Erro ao consultar processos no TJSP: {e}')

# Executa o programa com asyncio
if __name__ == "__main__":
    cpf = input("Digite o CPF/CNPJ: ").strip()
    nome = input("Digite o nome completo: ").strip()
    asyncio.run(consultar_processos(cpf, nome))
