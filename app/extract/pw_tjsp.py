from playwright.sync_api import sync_playwright
import time

URL = "https://esaj.tjsp.jus.br/cpopg/open.do"
FORO = "São Paulo"

def consultar_processos(cpf_cnpj: str, nome_completo: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def preencher_foro():
            page.get_by_role('link', name='Todos os foros').click()
            page.get_by_role('combobox', name='Foro').fill(FORO[:7])
            page.get_by_role('option', name=FORO, exact=True).locator('span').click()

        def consultar(tipo, campo, valor, msg_sem_processo) -> bool:
            page.goto(URL)
            page.get_by_label("Consultar por").select_option(tipo)
            page.locator(campo).fill(valor)
            preencher_foro()
            page.get_by_role('button', name='Consultar').click()
            mensagem = page.locator(f"text={msg_sem_processo}")
            try:
                mensagem.wait_for(timeout=4000)
                time.sleep(0.8)
                return False  # mensagem de "não encontrado" apareceu
            except:
                return True
        try:
            if consultar("DOCPARTE", "#campo_DOCPARTE", cpf_cnpj, "Não existem informações"):
                print(f'✅ Processos encontrados para o CPF/CNPJ: {cpf_cnpj}')
            elif consultar("NMPARTE", "#campo_NMPARTE", nome_completo, "Não existem informações disponíveis para os parâmetros informados."):
                print(f'✅ Processos encontrados para o nome: {nome_completo}')
            else:
                print('Nenhum processo localizado para o CPF/CNPJ ou nome informado.')
        except Exception as e:
            print(f'❌ Erro durante a consulta: {e}')

        browser.close()

if __name__ == "__main__":
    cpf = input("Digite o CPF/CNPJ: ").strip()
    nome = input("Digite o nome completo: ").strip()
    consultar_processos(cpf, nome)
