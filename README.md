# Projeto Argos — Checking Automático de Banners 

Automação inteligente com visão computacional (OCR) para auditoria, captura de tela e comprovação de veiculação publicitária (checking comercial).
*Inspirado em Argos Panoptes, o guardião de cem olhos que tudo vê e nunca dorme.*

---

## 📁 Estrutura do Projeto

```text
PrintAutomatico/
│
├── setup/                                 # Scripts de instalação e configuração
│   ├── setup_ambiente.bat                 # Cria a .venv e instala dependências
│   └── configurar_agendador.bat           # Agenda a execução diária no Windows
│
├── scripts/                               # Código-fonte principal do robô
│   ├── save_print.py                      # Orquestrador de navegação e checking
│   ├── config.py                          # Configurações de rotas, seletores e regras
│   ├── ocr_windows.py                     # Módulo Python de OCR nativo
│   └── win_ocr.ps1                        # Motor PowerShell (Windows.Media.Ocr)
│
├── testes/                                # Ambiente de testes e checking local (ignorado no Git)
│   ├── clientes_ativos.txt                # Lista de clientes em monitoramento
│   ├── robo_prints.log                    # Histórico detalhado de execução
│   └── regras_negocios.md                 # Regras de negócio e conformidade (RN001 a RN004)
│
├── executar_robo.bat                      # Disparo imediato do robô (1 clique na raiz)
├── clientes_ativos.txt.exemplo            # Modelo de lista de clientes
├── requirements.txt                       # Dependências Python do projeto
└── README.md                              # Documentação do projeto
```

---

## 🚀 Como Rodar em um Novo Computador

### Pré-requisitos:
- **Windows 10 ou 11**
- **Python 3.10+** instalado (marcando a opção *"Add python.exe to PATH"* no instalador)
- **Google Chrome** ou **Microsoft Edge** instalado

---

### Passo a Passo:

1. **Configurar o Ambiente**:
   - Dê dois cliques em [`setup/setup_ambiente.bat`](setup/setup_ambiente.bat).
   - Ele criará a `.venv` automaticamente e instalará as dependências (`playwright`, `pyautogui`, `pillow`).

2. **Definir os Clientes Ativos**:
   - Edite o arquivo `testes/clientes_ativos.txt` (ou crie na raiz) inserindo um cliente por linha:
     ```text
     unimed
     governo
     prefeitura
     ```

3. **Disparo Manual**:
   - Dê dois cliques em [`executar_robo.bat`](executar_robo.bat) na raiz do projeto a qualquer momento para rodar o robô.

4. **Agendamento Automático (Opcional)**:
   - Dê dois cliques em [`setup/configurar_agendador.bat`](setup/configurar_agendador.bat) e defina o horário desejado (ex: diariamente às 09:00).

---

## 🔍 Destaques Técnicos

- **OCR Nativo do Windows (`Windows.Media.Ocr`)**: Identifica marcas e patrocinadores diretamente da imagem do banner, mesmo quando não há links (`href`) ou textos descritivos no HTML.
- **Filtro de Placeholders**: Ignora automaticamente imagens genéricas (ex: `300-x-250px.png`, logos e placeholders de espaços vagos).
- **Conformidade com Regras de Negócio**:
  - **RN001**: Barra de tarefas do Windows visível com data e hora.
  - **RN002**: Barra de navegação visível com a URL completa.
  - **RN003**: Padronização dos arquivos em `[AAAA-MM-DD]_[CLIENTE].png`.
  - **RN004**: Logs salvos na pasta base da auditoria.
