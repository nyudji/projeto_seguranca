import asyncio
import logging
from playwright.async_api import async_playwright

class TJSP_Scraper:
    def __init__(self, cpf_cnpj: str, nome_completo: str):
        self.cpf_cnpj = cpf_cnpj
        self.nome_completo = nome_completo
        # O logger agora é obtido pela instância, não configurado aqui
        self.logger = logging.getLogger(__name__)
    
    # Métodos privados, indicados por _
    async def _preencher_secoes(self, page) -> None:
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
            self.logger.error(f"Nenhum link de foro ou seção foi encontrado: {e}")

    async def _consultar_instancia(self, page, tipo, campo, valor, msg_sem_processo, grau) -> bool:
        URL = "https://esaj.tjsp.jus.br/esaj/portal.do?servico=190090"
        await page.goto(URL)
        await page.get_by_role("cell", name=f"Consulta de Processos do {grau}ºGrau Consulta de Processos do {grau}ºGrau").get_by_role("link").click()
        await page.get_by_label("Consultar por").select_option(tipo)
        await page.locator(campo).fill(valor)
        await self._preencher_secoes(page)
        await page.get_by_role('button', name='Consultar').click()
        mensagem = page.locator(f"text={msg_sem_processo}")
        await asyncio.sleep(0.8)
        try:
            await mensagem.wait_for(timeout=4000)
            self.logger.info('Não encontrado processos')
            return False
        except:
            return True
        finally:
            await asyncio.sleep(0.8)

    async def _consultar_requisitorios(self, page, tipo, campo, valor, msg_sem_processo) -> bool:
        URL = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do"
        await page.goto(URL)
        await page.get_by_label("Consultar por").select_option(tipo)
        await page.locator(campo).fill(valor)
        await page.get_by_role('button', name='Consultar').click()
        mensagem = page.locator(f"text={msg_sem_processo}")
        await asyncio.sleep(0.8)
        try:
            await mensagem.wait_for(timeout=4000)
            self.logger.info('Não encontrado requisitórios')
            return False
        except:
            return True
        finally:
            await asyncio.sleep(0.8)

    # Método público que orquestra a execução, agora chamado de `run`
    async def run(self) -> None:
        '''Função para consultar processos no TJSP usando Playwright.'''
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                self.logger.info("Iniciando consulta de processos no TJSP")

                # 1º grau
                try:
                    if await self._consultar_instancia(page, "DOCPARTE", "#campo_DOCPARTE", self.cpf_cnpj, "Não existem informações", 1):
                        self.logger.info(f'Processos encontrados para o CPF/CNPJ: {self.cpf_cnpj}')
                    elif await self._consultar_instancia(page, "NMPARTE", "#campo_NMPARTE", self.nome_completo, "Não existem informações disponíveis para os parâmetros informados.", 1):
                        self.logger.info(f'Processos encontrados para o nome: {self.nome_completo} - 1º grau')
                    else:
                        self.logger.info('Nenhum processo localizado - 1º grau')
                except Exception as e:
                    self.logger.error(f'❌ Erro durante a consulta processos 1º grau: {e}')

                # 2º grau
                try:
                    if await self._consultar_instancia(page, "DOCPARTE", "#campo_DOCPARTE", self.cpf_cnpj, "Não existem informações", 2):
                        self.logger.info(f'Processos encontrados para o CPF/CNPJ: {self.cpf_cnpj} - 2º grau')
                    elif await self._consultar_instancia(page, "NMPARTE", "#campo_NMPARTE", self.nome_completo, "Não existem informações disponíveis para os parâmetros informados.", 2):
                        self.logger.info(f'Processos encontrados para o nome: {self.nome_completo} - 2º grau')
                    else:
                        self.logger.info('Nenhum processo localizado - 2º grau')
                except Exception as e:
                    self.logger.error(f'❌ Erro durante a consulta processos 2º grau: {e}')

                # Consulta de requisitórios
                self.logger.info("Iniciando consulta de requisitórios")
                await asyncio.sleep(0.8)
                try:
                    if await self._consultar_requisitorios(page, "DOCPARTE", "#campo_DOCPARTE", self.cpf_cnpj, "Não existem informações disponíveis para os parâmetros informados."):
                        self.logger.info(f'Requisitorios encontrados para o CPF/CNPJ: {self.cpf_cnpj} - Repositórios')
                except Exception as e:
                    self.logger.error(f'❌ Erro durante a consulta de requisitórios: {e}')      

                # Fechando o navegador
                await browser.close()
                self.logger.info("Consulta finalizada.")

        except Exception as e:
            self.logger.error(f'Erro ao consultar processos no TJSP: {e}')
