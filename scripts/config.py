import os
from pathlib import Path

# =========================================================================
# CONFIGURAÇÕES DE DIRETÓRIOS E ROTAS
# =========================================================================
# Diretório local do projeto (raiz)
DIRETORIO_PROJETO = Path(__file__).resolve().parent.parent

# URLs e Portais
URL_ALVO = os.getenv("URL_ALVO", "https://98fmnatal.com.br/")

# Caminhos de Armazenamento e Arquivos de Entrada (Rede / Local)
PASTA_BASE_CHECKING = os.getenv("PASTA_BASE_CHECKING", str(DIRETORIO_PROJETO / "testes"))
CAMINHO_CLIENTES = os.getenv(
    "CAMINHO_CLIENTES", 
    os.path.join(PASTA_BASE_CHECKING, "clientes_ativos.txt")
)

# Caminho do Arquivo de Log (salvo diretamente na pasta base)
CAMINHO_LOG = os.path.join(PASTA_BASE_CHECKING, "robo_prints.log")

# =========================================================================
# PARÂMETROS DE EXECUÇÃO E AUTOMAÇÃO
# =========================================================================
LIMITE_RODADAS = 15

# Timeouts do Playwright (em milissegundos)
TIMEOUT_NAVEGACAO_MS = 60000
TIMEOUT_INTERACAO_MS = 3000
TEMPO_ESPERA_ANIMACAO_MS = 3000  # Tempo para GIFs/transições carregarem antes do print

# Seletores CSS do DOM
SELETORES_BANNERS = (
    '.anuncio_sidebar_post, [class*="anuncio"], [class*="banner"], '
    'a:has(picture), a:has(img), '
    'picture img, img'
)
SELETORES_LINKS_NOTICIAS = 'h2 a, h3 a, .post-title a'
SELETORES_CONSENTIMENTO_COOKIES = "text=/aceitar|concordar|prosseguir|entendi|ok/i"

# Termos para ignorar elementos que não são anúncios de clientes (placeholders, logos, ícones)
TERMOS_IGNORAR_BANNERS = [
    "300-x-250",
    "300x250",
    "placeholder",
    "anuncie-aqui",
    "espaco-publicitario",
    "logo",
    "icon",
    "avatar",
    "whatsapp",
    "instagram",
    "facebook",
    "youtube",
    "twitter",
]
