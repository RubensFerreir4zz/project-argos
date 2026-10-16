import subprocess
import os
import tempfile
import logging

CAMINHO_SCRIPT_PS1 = os.path.join(os.path.dirname(__file__), "win_ocr.ps1")

def extrair_texto_imagem_nativo(caminho_imagem: str) -> str:
    """
    Usa o motor de OCR nativo do Windows 10/11 (Windows.Media.Ocr)
    chamando o script PowerShell dedicado win_ocr.ps1.
    """
    if not os.path.exists(caminho_imagem) or not os.path.exists(CAMINHO_SCRIPT_PS1):
        return ""

    try:
        caminho_absoluto = os.path.abspath(caminho_imagem)
        process = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                CAMINHO_SCRIPT_PS1,
                "-ImagePath",
                caminho_absoluto,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=15,
        )

        if process.returncode == 0:
            return process.stdout.strip()
        else:
            logging.debug(f"Aviso no OCR nativo: {process.stderr.strip()}")
            return ""

    except Exception as erro:
        logging.error(f"Erro ao executar OCR nativo do Windows: {erro}")
        return ""


if __name__ == "__main__":
    from PIL import Image, ImageDraw, ImageFont

    print("Testando OCR Nativo do Windows chamando win_ocr.ps1...")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        caminho_tmp = tmp.name

    try:
        img = Image.new("RGB", (600, 250), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        fonte = None
        for f in ["C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\segoeui.ttf"]:
            if os.path.exists(f):
                try:
                    fonte = ImageFont.truetype(f, 36)
                    break
                except Exception:
                    pass

        draw.text((40, 70), "UNIMED NATAL", fill=(0, 128, 0), font=fonte)
        draw.text((40, 130), "CUIDAR DE VOCÊ", fill=(50, 50, 50), font=fonte)
        img.save(caminho_tmp)

        print(f"Imagem gerada: {caminho_tmp}")
        texto = extrair_texto_imagem_nativo(caminho_tmp)
        print(f"Texto reconhecido pelo OCR nativo:\n---\n{texto}\n---")
        if "unimed" in texto.lower():
            print(">>> SUCESSO TOTAL: O OCR nativo reconheceu o cliente perfeitamente! <<<")
        else:
            print(">>> AVISO: O texto não correspondeu ao esperado. <<<")
    finally:
        if os.path.exists(caminho_tmp):
            os.remove(caminho_tmp)
