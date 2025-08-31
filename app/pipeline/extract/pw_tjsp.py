import asyncio
import logging
from playwright.async_api import async_playwright

class TJSP_Scraper:
    def __init__(self, cpf: str, nome_completo: str):
        """Inicializa o scraper TJSP """
        self.cpf = cpf
        self.nome_completo = nome_completo
        self.logger = logging.getLogger(__name__)
        self.resultado = {
            "funcionario": {
                "cpf": self.cpf,
                "nome": self.nome_completo
            },
            "processos": []
        }
        self.tem_processos_encontrados = False
    
    async def _preencher_secoes(self, page) -> None:
        '''Função para preencher as seções ou foros na página de consulta.'''
        FORO = "Todos os foros"
        try:
            link_foros = page.get_by_role("link", name="Todos os foros")
            await asyncio.sleep(0.8)
            if await link_foros.is_visible():
                await link_foros.click()
                await page.get_by_role('combobox', name='Foro').fill(FORO[:7])
                await page.get_by_role('option', name=FORO, exact=True).locator('span').click()
            else:
                await page.get_by_role("link", name="Todas as seções").click()
                await page.get_by_role("option", name="Todas as seções").click()
        except Exception as e:
            self.logger.error(f"Nenhum link de foro ou seção foi encontrado: {e}")

    async def _extrair_dados_processos(self, page, grau: int) -> list:
        '''
        Nova função para extrair os dados da tabela de processos.
        Retorna uma lista de dicionários com os detalhes de cada processo.
        '''
        processos_encontrados = []
        try:
            # Localiza a tabela de processos e as linhas
            tabela = page.locator("#resultadosTable")
            linhas = await tabela.locator("tr.unj-table__row").all()

            for linha in linhas:
                # Extrai os dados de cada célula da linha
                colunas = await linha.locator("td").all()
                if len(colunas) > 0:
                    numero_processo = await colunas[0].inner_text()
                    classe = await colunas[1].inner_text()
                    assunto = await colunas[2].inner_text()
                    data_distribuicao = await colunas[3].inner_text()
                    
                    # Crie a lógica para determinar o risco aqui
                    # Exemplo simples: Risco mais alto para "criminal"
                    risco = 0
                    if "crime" in assunto.lower() or "criminal" in classe.lower():
                        risco = 5 # Risco alto
                    elif "execução fiscal" in assunto.lower():
                        risco = 3 # Risco médio
                    else:
                        risco = 1 # Risco baixo

                    processos_encontrados.append({
                        "numero_processo": numero_processo.strip(),
                        "grau": grau,
                        "classe": classe.strip(),
                        "assunto": assunto.strip(),
                        "data_distribuicao": data_distribuicao.strip(),
                        "fonte": "TJSP",
                        "risco": risco,
                        "descricao": f"Processo de {classe.strip()} com assunto {assunto.strip()}."
                    })
            self.logger.info(f" {len(processos_encontrados)} processo(s) extraído(s) para o {grau}º grau.")
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair dados da tabela: {e}")

        return processos_encontrados

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
            self.logger.info(f'Processos encontrados para o {grau}º grau. Extraindo dados...')
            processos = await self._extrair_dados_processos(page, grau)
            self.resultado["processos"].extend(processos) # Adiciona os processos à lista do objeto
            self.tem_processos_encontrados = True
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
            self.logger.info('Encontrado requisitórios')
            return True
        finally:
            await asyncio.sleep(0.8)

    async def run(self) -> None:
        '''Função para consultar processos no TJSP usando Playwright.'''
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                self.logger.info("Iniciando consulta de processos no TJSP")

                # 1º grau
                try:
                    if await self._consultar_instancia(page, "DOCPARTE", "#campo_DOCPARTE", self.cpf, "Não existem informações", 1):
                        self.logger.info(f'Processos encontrados para o CPF/CNPJ: {self.cpf}')
                    elif await self._consultar_instancia(page, "NMPARTE", "#campo_NMPARTE", self.nome_completo, "Não existem informações disponíveis para os parâmetros informados.", 1):
                        self.logger.info(f'Processos encontrados para o nome: {self.nome_completo} - 1º grau')
                    else:
                        self.logger.info('Nenhum processo localizado - 1º grau')
                except Exception as e:
                    self.logger.error(f'❌ Erro durante a consulta processos 1º grau: {e}')

                # 2º grau
                try:
                    if await self._consultar_instancia(page, "DOCPARTE", "#campo_DOCPARTE", self.cpf, "Não existem informações", 2):
                        self.logger.info(f'Processos encontrados para o CPF/CNPJ: {self.cpf} - 2º grau')
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
                    if await self._consultar_requisitorios(page, "DOCPARTE", "#campo_DOCPARTE", self.cpf, "Não existem informações disponíveis para os parâmetros informados."):
                        self.logger.info(f'Requisitorios encontrados para o CPF/CNPJ: {self.cpf} - Repositórios')
                except Exception as e:
                    self.logger.error(f'❌ Erro durante a consulta de requisitórios: {e}')      

                # Fechando o navegador
                await browser.close()
                self.logger.info("Consulta finalizada.")

        except Exception as e:
            self.logger.error(f'Erro ao consultar processos no TJSP: {e}')
        # Lógica final para determinar o estado e o risco geral
        if not self.tem_processos_encontrados:
             self.resultado["processos"].append({
                "risco": 0,
                "fonte": "TJSP",
                "descricao": "Nenhum processo encontrado."
            })
        
        # Retorna o resultado final
        return self.resultado