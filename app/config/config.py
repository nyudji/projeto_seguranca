from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
RAIZ_PROJETO = Path(__file__).resolve().parents[1]
logger.info(f"RAIZ_PROJETO está na : {RAIZ_PROJETO}")

DIRETORIO_DADOS = RAIZ_PROJETO  / "data"
DIRETORIO_DADOS_BRUTOS = DIRETORIO_DADOS / "bruto"
DIRETORIO_DADOS_INTERMEDIARIOS = DIRETORIO_DADOS / "interno"
DIRETORIO_DADOS_PROCESSADOS = DIRETORIO_DADOS / "tratado"
DIRETORIO_DADOS_EXTERNOS = DIRETORIO_DADOS / "externo"

DIRETORIO_MODELOS = RAIZ_PROJETO / "modelos"

DIRETORIO_RELATORIOS = RAIZ_PROJETO / "relatorios"
DIRETORIO_FIGURAS = DIRETORIO_RELATORIOS  / "figuras"

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
