import datetime
import logging
import os
import re
import sys
import tempfile
import pyautogui
from playwright.sync_api import sync_playwright
import config
from ocr_windows import extrair_texto_imagem_nativo

# =========================================================================
# CONFIGURAÇÃO DE LOGS (SALVO NA PASTA BASE)
# =========================================================================
try:
    os.makedirs(config.PASTA_BASE_CHECKING, exist_ok=True)
    caminho_log_efetivo = config.CAMINHO_LOG
except Exception as erro_pasta:
    caminho_log_efetivo = os.path.join(config.DIRETORIO_PROJETO, "robo_prints.log")
    print(f"[AVISO] Não foi possível acessar a pasta base para o log ({config.PASTA_BASE_CHECKING}). Usando log local: {erro_pasta}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(caminho_log_efetivo, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

# =========================================================================
# UTILITÁRIOS E GERENCIAMENTO DE ARQUIVOS
# =========================================================================
def sanitizar_nome(nome: str) -> str:
    """Remove caracteres especiais e substitui espaços por underscores."""
    nome_limpo = re.sub(r"[^a-zA-Z0-9_\-\s]", "", nome)
    return re.sub(r"\s+", "_", nome_limpo).strip("_")


def carregar_clientes_ativos(caminho_arquivo: str) -> list[str]:
    """Lê o arquivo de texto contendo a lista de clientes para auditoria, com fallback local."""
    caminho_final = caminho_arquivo
    if not os.path.exists(caminho_final):
        # Tenta encontrar clientes_ativos.txt localmente na pasta testes ou na raiz
        caminho_testes = os.path.join(config.DIRETORIO_PROJETO, "testes", "clientes_ativos.txt")
        caminho_raiz = os.path.join(config.DIRETORIO_PROJETO, "clientes_ativos.txt")
        if os.path.exists(caminho_testes):
            caminho_final = caminho_testes
            logging.info(f"Usando lista de clientes da pasta testes: {caminho_testes}")
        elif os.path.exists(caminho_raiz):
            caminho_final = caminho_raiz
            logging.info(f"Usando lista de clientes da raiz: {caminho_raiz}")
        else:
            logging.error(f"Arquivo de clientes não encontrado ({caminho_arquivo}) nem localmente.")
            return []

    with open(caminho_final, "r", encoding="utf-8") as f:
        clientes = [linha.strip() for linha in f if linha.strip()]

    logging.info(f"Lista de clientes carregada ({len(clientes)} clientes): {caminho_final}")
    return clientes


def capturar_tela_checking(nome_patrocinador: str, tipo_contexto: str = "") -> tuple[bool, str | None]:
    """
    Salva o print da tela cheia para atender as regras de negócio:
    - RN001: Barra de ferramentas do S.O. visível (data/hora do sistema).
    - RN002: Barra de endereços do navegador visível (URL completa).
    - RN003: Nome do arquivo no padrão [ANO-MES-DIA]_[NOME_CLIENTE]_[TIPO].png.
    """
    nome_limpo = sanitizar_nome(nome_patrocinador)
    agora_dt = datetime.datetime.now()
    mes_ano = agora_dt.strftime("%Y-%m")
    data_str = agora_dt.strftime("%Y-%m-%d")

    # Define a pasta base (usa pasta local se a rede Z: não estiver acessível)
    pasta_base = config.PASTA_BASE_CHECKING
    try:
        os.makedirs(pasta_base, exist_ok=True)
    except Exception:
        pasta_base = os.path.join(config.DIRETORIO_PROJETO, "testes")
        os.makedirs(pasta_base, exist_ok=True)

    # Estrutura: PASTA_BASE / AAAA-MM / Nome_Cliente / AAAA-MM-DD_Nome_Cliente_[Tipo].png
    pasta_cliente = os.path.join(pasta_base, mes_ano, nome_limpo)
    os.makedirs(pasta_cliente, exist_ok=True)

    sufixo_tipo = f"_{tipo_contexto}" if tipo_contexto else ""
    nome_arquivo = f"{data_str}_{nome_limpo}{sufixo_tipo}.png"
    caminho_completo = os.path.join(pasta_cliente, nome_arquivo)

    try:
        # Move o cursor do mouse para lateral para não sobrepor o banner ou abrir hovers
        largura_tela, altura_tela = pyautogui.size()
        pyautogui.moveTo(5, altura_tela // 2)

        # Captura da tela inteira (inclui barra de endereços do browser e barra do Windows)
        pyautogui.screenshot(caminho_completo)
        logging.info(f"✅ Print salvo com sucesso: {caminho_completo}")
        return True, nome_limpo
    except Exception as erro:
        logging.error(f"❌ Erro ao capturar print de '{nome_patrocinador}': {erro}")
        return False, None


# =========================================================================
# SCANNER DO DOM (IDENTIFICAÇÃO DE BANNERS)
# =========================================================================
def eh_banner_placeholder(srcs: list[str]) -> bool:
    """Verifica se todas as imagens detectadas pertencem à lista de exclusão/placeholder."""
    termos_ignorar = getattr(config, "TERMOS_IGNORAR_BANNERS", [])
    if not termos_ignorar or not srcs:
        return False

    for src in srcs:
        src_lower = src.lower()
        if not any(termo in src_lower for termo in termos_ignorar):
            return False  # Pelo menos uma imagem não é placeholder
    return True


def escanear_banners_na_pagina(pagina, contexto_nome: str, pendentes: set[str], capturados: set[str], tipo_contexto: str = ""):
    """
    Varre os elementos de imagem, contêineres (.anuncio_sidebar_post) e links da página.
    Aplica extração profunda de atributos, filtro de placeholders e fallback para OCR nativo.
    """
    logging.info(f"🔎 Escaneando banners em: {contexto_nome}")
    elementos = pagina.locator(config.SELETORES_BANNERS).all()

    for elemento in elementos:
        try:
            # Verifica se o elemento está visível na tela
            if not elemento.is_visible():
                continue

            # Extração profunda de metadados do elemento (filhos e ancestrais)
            dados = elemento.evaluate("""el => {
                let imgs = el.tagName === 'IMG' ? [el] : Array.from(el.querySelectorAll('img'));
                let links = [];
                if (el.tagName === 'A') {
                    links.push(el);
                } else {
                    let parentA = el.closest('a');
                    if (parentA) links.push(parentA);
                    links.push(...Array.from(el.querySelectorAll('a')));
                }

                let srcs = imgs.map(i => i.currentSrc || i.src || '').filter(Boolean);
                let alts = imgs.map(i => i.alt || '').filter(Boolean);
                let titles = [el.title || '']
                    .concat(imgs.map(i => i.title || ''))
                    .concat(links.map(l => l.title || ''))
                    .filter(Boolean);
                let hrefs = links.map(l => l.href || '').filter(Boolean);

                return {
                    srcs: srcs,
                    alts: alts,
                    titles: titles,
                    hrefs: hrefs,
                    tem_imagem: imgs.length > 0
                };
            }""")

            srcs = dados.get("srcs", [])
            alts = dados.get("alts", [])
            titles = dados.get("titles", [])
            hrefs = dados.get("hrefs", [])
            tem_imagem = dados.get("tem_imagem", False)

            # 1. Descarta elementos que são puramente placeholders / espaços vagos
            if eh_banner_placeholder(srcs):
                continue

            texto_contexto = " ".join(alts + titles + srcs + hrefs).lower().strip()
            nome_detectado = None
            alvo_original = None
            metodo_identificacao = None

            # 2. Busca nos metadados e URLs (src, href, alt, title)
            if texto_contexto:
                for alvo in list(pendentes):
                    alvo_lower = alvo.lower()
                    alvo_norm = re.sub(r"[^a-z0-9]", "", alvo_lower)
                    texto_norm = re.sub(r"[^a-z0-9]", "", texto_contexto)

                    if alvo_lower in texto_contexto or (alvo_norm and alvo_norm in texto_norm):
                        nome_detectado = alvo.title()
                        alvo_original = alvo
                        metodo_identificacao = "Metadados / URL"
                        break

            # 3. Fallback: OCR Nativo do Windows (quando não há texto na URL/HTML)
            if not nome_detectado and tem_imagem:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    caminho_tmp_banner = tmp_file.name

                try:
                    elemento.screenshot(path=caminho_tmp_banner, timeout=config.TIMEOUT_INTERACAO_MS)
                    texto_ocr = extrair_texto_imagem_nativo(caminho_tmp_banner).lower()
                    if texto_ocr:
                        texto_ocr_norm = re.sub(r"[^a-z0-9]", "", texto_ocr)
                        for alvo in list(pendentes):
                            alvo_lower = alvo.lower()
                            alvo_norm = re.sub(r"[^a-z0-9]", "", alvo_lower)

                            if alvo_lower in texto_ocr or (alvo_norm and alvo_norm in texto_ocr_norm):
                                nome_detectado = alvo.title()
                                alvo_original = alvo
                                metodo_identificacao = f"OCR Nativo (Texto lido: '{texto_ocr[:30]}...')"
                                break
                except Exception as erro_ocr:
                    logging.debug(f"Aviso no fallback OCR: {erro_ocr}")
                finally:
                    if os.path.exists(caminho_tmp_banner):
                        try:
                            os.remove(caminho_tmp_banner)
                        except Exception:
                            pass

            if not nome_detectado:
                continue

            nome_limpo = sanitizar_nome(nome_detectado)
            chave_captura = f"{nome_limpo}_{tipo_contexto}" if tipo_contexto else nome_limpo
            if chave_captura in capturados:
                continue

            logging.info(f"🎯 Banner detectado [{tipo_contexto}]: {nome_detectado} [Método: {metodo_identificacao}]")

            # Centraliza o elemento no meio da tela para visibilidade clara no print
            try:
                elemento.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
            except Exception as scroll_err:
                logging.warning(f"Fallback no scrollIntoView: {scroll_err}")
                elemento.scroll_into_view_if_needed(timeout=config.TIMEOUT_INTERACAO_MS)

            # Aguarda a rolagem e o carregamento completo do criativo (GIFs, animações)
            pagina.wait_for_timeout(config.TEMPO_ESPERA_ANIMACAO_MS)
            pagina.bring_to_front()

            # Captura de tela cheia (RN001, RN002, RN003)
            sucesso, id_capturado = capturar_tela_checking(nome_detectado, tipo_contexto=tipo_contexto)
            if sucesso:
                capturados.add(chave_captura)
                if alvo_original:
                    pendentes.discard(alvo_original)
                    logging.info(f"✔️ CHECKLIST [{tipo_contexto.upper()}]: {alvo_original.upper()} concluído com sucesso.")

        except Exception:
            continue


# =========================================================================
# NAVEGAÇÃO E PROCESSAMENTO DE PÁGINAS
# =========================================================================
def processar_pagina_home(pagina, pendentes: set[str], capturados: set[str], rodada: int):
    """Navega pela Home Page, lidando com lazy-load e consentimento."""
    logging.info(f"🏠 Iniciando processamento da HOME (Rodada {rodada})")

    try:
        pagina.goto(config.URL_ALVO, timeout=config.TIMEOUT_NAVEGACAO_MS, wait_until="domcontentloaded")
        pagina.wait_for_timeout(config.TIMEOUT_INTERACAO_MS)

        # Lida com aviso de cookies/LGPD na primeira rodada
        if rodada == 1:
            try:
                pagina.locator(config.SELETORES_CONSENTIMENTO_COOKIES).first.click(
                    timeout=config.TIMEOUT_INTERACAO_MS
                )
            except Exception:
                pass

        # Força lazy-load rolando a página em passos progressivos
        for _ in range(10):
            pagina.evaluate("window.scrollBy(0, 800)")
            pagina.wait_for_timeout(400)

        pagina.evaluate("window.scrollTo(0, 0)")
        pagina.wait_for_timeout(1000)

        escanear_banners_na_pagina(pagina, "Home Page", pendentes, capturados, tipo_contexto="Home")

    except Exception as erro:
        logging.error(f"Erro ao processar Home: {erro}")


def processar_noticia_interna(pagina, pendentes: set[str], capturados: set[str], rodada: int):
    """Navega por notícias internas para capturar banners rotativos e laterais."""
    logging.info(f"📰 Iniciando processamento de NOTÍCIA INTERNA (Rodada {rodada})")

    try:
        if pagina.url != config.URL_ALVO:
            pagina.goto(config.URL_ALVO, timeout=config.TIMEOUT_NAVEGACAO_MS, wait_until="domcontentloaded")

        links = pagina.locator(config.SELETORES_LINKS_NOTICIAS).all()
        if not links:
            logging.warning("Nenhum link de notícia encontrado na página.")
            return

        # Alterna dinamicamente a notícia com base no número da rodada
        indice = (rodada - 1) % len(links)
        url_noticia = links[indice].get_attribute("href")

        logging.info(f"Navegando para notícia #{indice + 1}: {url_noticia}")
        pagina.goto(url_noticia, timeout=config.TIMEOUT_NAVEGACAO_MS, wait_until="domcontentloaded")
        pagina.wait_for_timeout(2000)

        # Rolagem progressiva para acionar banners de sidebar (.anuncio_sidebar_post) e meio de matéria
        for _ in range(6):
            pagina.evaluate("window.scrollBy(0, 600)")
            pagina.wait_for_timeout(500)

        escanear_banners_na_pagina(pagina, f"Notícia #{indice + 1}", pendentes, capturados, tipo_contexto="Noticia")

    except Exception as erro:
        logging.error(f"Erro ao processar notícia interna: {erro}")


# =========================================================================
# ORQUESTRADOR PRINCIPAL
# =========================================================================
def main():
    logging.info("=== ARGOS | INICIANDO ROTINA AUTOMATIZADA DE CHECKING ===")

    clientes_ativos = carregar_clientes_ativos(config.CAMINHO_CLIENTES)
    if not clientes_ativos:
        logging.warning("Operação abortada: nenhum cliente ativo carregado para busca.")
        return

    # Mantém checklists separados: comprovação na Home e na Notícia interna
    pendentes_home = set(c.lower() for c in clientes_ativos)
    pendentes_noticia = set(c.lower() for c in clientes_ativos)
    capturados = set()
    rodada = 1

    with sync_playwright() as p:
        # Prioriza o Google Chrome nativo do Windows, com fallback para Edge ou Chromium
        try:
            browser = p.chromium.launch(channel="chrome", headless=False, args=["--start-maximized"])
        except Exception:
            try:
                browser = p.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
            except Exception:
                browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        pagina = context.new_page()

        while rodada <= config.LIMITE_RODADAS:
            if not pendentes_home and not pendentes_noticia:
                logging.info("🎯 Todos os clientes alvo foram capturados na Home e nas Notícias!")
                break

            logging.info(f"\n--- RODADA {rodada} DE {config.LIMITE_RODADAS} ---")
            logging.info(f"Pendências: {len(pendentes_home)} na Home | {len(pendentes_noticia)} em Notícias")

            # 1. Se ainda houver pendentes na Home, processa a Home
            if pendentes_home:
                processar_pagina_home(pagina, pendentes_home, capturados, rodada)

            # 2. Se ainda houver pendentes em Notícias, processa notícias internas
            if pendentes_noticia:
                processar_noticia_interna(pagina, pendentes_noticia, capturados, rodada)

            rodada += 1

        browser.close()
        logging.info(f"=== ARGOS | FIM DA OPERAÇÃO. Total de capturas realizadas: {len(capturados)} ===")


if __name__ == "__main__":
    main()