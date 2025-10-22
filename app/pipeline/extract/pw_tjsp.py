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
            # Verifica se existe o link "Todos os foros"
            link_foros = page.get_by_role("link", name="Todos os foros")
            if await link_foros.count() > 0 and await link_foros.is_visible():
                await asyncio.sleep(0.8)
                await link_foros.click()
                await page.get_by_role('combobox', name='Foro').fill(FORO[:7])
                await page.get_by_role('option', name=FORO, exact=True).locator('span').click()
            else:
                # Verifica se existe o link "Todas as seções"
                link_secoes = page.get_by_role("link", name="Todas as seções")
                if await link_secoes.count() > 0 and await link_secoes.is_visible():
                    await link_secoes.click()
                    await page.get_by_role("option", name="Todas as seções").click()
                else:
                    self.logger.info("Nenhum filtro de foro ou seção disponível na página. Prosseguindo sem seleção.")
        except Exception as e:
            self.logger.error(f"Nenhum link de foro ou seção foi encontrado: {e}")
            
    async def _extrair_dados_processos(self, page, grau: int) -> list:
        processos_encontrados = []
        try:
            # Aguarda o carregamento da lista de processos
            await page.wait_for_selector("#listagemDeProcessos a.linkProcesso", timeout=10000)
            links = await page.locator("#listagemDeProcessos a.linkProcesso").all()
            for link in links:
                numero_processo = (await link.inner_text()).strip()
                div_pai = link.locator("xpath=ancestor::div[contains(@class, 'row')]")
                # Extrai classe
                classe = await div_pai.locator(".classeProcesso").inner_text() if await div_pai.locator(".classeProcesso").count() else ""
                # Extrai assunto
                assunto = await div_pai.locator(".assuntoPrincipalProcesso").inner_text() if await div_pai.locator(".assuntoPrincipalProcesso").count() else ""
                # Extrai data de distribuição
                data_distribuicao = await div_pai.locator(".dataLocalDistribuicaoProcesso").inner_text() if await div_pai.locator(".dataLocalDistribuicaoProcesso").count() else ""
                # Extrai nome da parte (opcional)
                nome_parte = await div_pai.locator(".nomeParte").inner_text() if await div_pai.locator(".nomeParte").count() else ""

                # Lógica de risco (ajuste conforme sua regra)
                risco = 0
                if "crime" in assunto.lower() or "criminal" in classe.lower():
                    risco = 5
                elif "execução fiscal" in assunto.lower():
                    risco = 3
                else:
                    risco = 1

                processos_encontrados.append({
                    "numero_processo": numero_processo,
                    "grau": grau,
                    "classe": classe,
                    "assunto": assunto,
                    "data_distribuicao": data_distribuicao,
                    "nome_parte": nome_parte,
                    "fonte": "TJSP",
                    "risco": risco,
                    "descricao": f"Processo de {classe} com assunto {assunto}."
                })
            self.logger.info(f"{len(processos_encontrados)} processo(s) extraído(s) para o {grau}º grau.")
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair dados da lista: {e}")
        return processos_encontrados

    async def _consultar_instancia(self, page, tipo, campo, valor, msg_sem_processo, grau) -> bool:
        URL = "https://esaj.tjsp.jus.br/esaj?servico=190090"
        await page.goto(URL)
        await page.get_by_role("link", name=f"Consulta de Processos do {grau}º").click()
        await page.get_by_label("Consultar por").select_option(tipo)
        await page.locator(campo).fill(valor)
        await self._preencher_secoes(page)
        await page.get_by_role('button', name='Consultar').click()
        mensagem = page.locator(f"text={msg_sem_processo}")
        mensagem_muitos = page.locator("text=Foram encontrados muitos processos para os parâmetros informados. Por favor, refine sua busca.")
        await asyncio.sleep(1)
        try:
            await mensagem.wait_for(timeout=4000)
            self.logger.info('Não encontrado processos')
            return False
        except:
        
            try:
                # Verifica se apareceu a mensagem de muitos processos
                await mensagem_muitos.wait_for(timeout=2000)
                self.logger.info('Muitos processos encontrados, refinando busca para foro "São Paulo"...')
                # Seleciona o foro "São Paulo" e tenta novamente
                await page.get_by_role("link", name="Todos os foros").click()
                await page.get_by_role('combobox', name='Foro').fill("São Paulo")
                await page.get_by_role('option', name="São Paulo", exact=True).locator('span').click()
                await page.get_by_role('button', name='Consultar').click()
                await asyncio.sleep(1)
                # Tenta extrair processos novamente
                processos = await self._extrair_dados_processos(page, grau)
                if processos:
                    self.resultado["processos"].extend(processos)
                    self.tem_processos_encontrados = True
                    return True
                else:
                    self.logger.info('Nenhum processo localizado após refinar para foro "São Paulo".')
                    return False
            except:
                self.logger.info(f'Processos encontrados para o {grau}º grau. Extraindo dados...')
                processos = await self._extrair_dados_processos(page, grau)
                self.resultado["processos"].extend(processos)
                self.tem_processos_encontrados = True
                return True
        finally:
            await asyncio.sleep(0.8)

    async def _consultar_requisitorios(self, page, tipo, campo, valor, msg_sem_processo) -> bool:
        URL = "https://esaj.tjsp.jus.br/cpopg/abrirConsultaDeRequisitorios.do"
        await page.goto(URL)
        await page.get_by_label("Consultar por").select_option(tipo)
        await asyncio.sleep(0.8)
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
                        await asyncio.sleep(0.8)
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