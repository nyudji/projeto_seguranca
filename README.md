# Projeto Segurança

<div align="right">
  <a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
  </a>
</div>

Projeto de estágio focado na criação de uma ferramenta de análise para identificar anomalias, dados suspeitos e potenciais riscos que possam impactar a integridade e a reputação da empresa

## Arquitetura
<img width="1552" height="824" alt="image" src="https://github.com/user-attachments/assets/57ddd75f-5ef1-461d-9fa9-ddb2fa56f73a" />





## Estrutura

```
├── LICENSE            <- Licença de código aberto, caso uma seja escolhida.
├── Makefile           <- Arquivo com comandos úteis, como `make data` ou `make train`.
├── README.md          <- O arquivo de introdução principal para desenvolvedores que usam este projeto.
│
├── docs               <- Um projeto padrão do MkDocs; veja www.mkdocs.org para detalhes.
│
├── modelos             <- Modelos treinados e serializados, previsões de modelos ou resumos de modelos.
│
├── notebooks          <- Notebooks Jupyter. A convenção de nomeação é um número (para ordenação),
│                         as iniciais do criador e uma breve descrição, por exemplo:
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Arquivo de configuração do projeto com metadados do pacote e configurações para
│                         ferramentas como o Black e o Ruff.
│
├── references         <- Dicionários de dados, manuais e outros materiais explicativos.
│
├── relatorios            <- Análises geradas em HTML, PDF, LaTeX, etc.
│   └── figuras        <- Gráficos e figuras geradas para uso nos relatórios.
│
├── requirements.txt   <- O arquivo de requisitos para reproduzir o ambiente de análise, por exemplo,
│                      
│
├── setup.cfg          <- Arquivo de configuração para o Flake8.
│
└── app                <- Código-fonte para uso neste projeto.
    │
    ├── __init__.py             <- Transforma 'app' em um módulo Python.
    │
    ├── config                  <- Armazena variáveis úteis e configurações.
    │
    ├── dados
    │    ├── externo       <- Dados de fontes externas (APIs, bancos de dados, etc.).
    │    ├── interno        <- Dados intermediários que já foram transformados.
    │    ├── tratado      <- Conjuntos de dados finais e padronizados para modelagem.
    │    └── bruto            <- O despejo de dados original e imutável.
    │
    ├── db                      <- Configurações e funcoes banco de dados.
    │
    ├── pipeline
    │       ├── extract                 <- Scripts para extrair dados de diferentes fontes.
    │       ├── processing              <- Código para limpar, processar e transformar dados brutos.
    │       ├── load                    <- Scripts para carregar dados.
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Código para executar inferência com modelos treinados.          
    │   └── train.py            <- Código para treinar modelos.
    │
    └── front                    <- Frontend, Dataviz

```
## Passo a passo

Siga os passos abaixo para configurar o ambiente de desenvolvimento e instalar as dependências do projeto.

### 1. Criar o Ambiente Virtual

Crie um ambiente virtual para isolar as dependências do projeto.

```bash
python -m venv .venv
```
### 2. Atualizar pip 

Realizar upgrade no pip

```bash
python.exe -m pip install --upgrade pip     
```

### 3. Instalar 

Instalar bibliotecas necesárias

```bash
pip install -r requirements.txt       
```

### 4. Ativando Playwright

```bash
playwright install
```


--------

