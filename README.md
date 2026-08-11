# LIBRYNO v2.0

Sistema de Gestão de Biblioteca Pública integrado ao ecossistema **OrdoB**.

## Instalação

### Opção 1: Executável Pronto (Recomendado)

#### Windows
1. Acesse a [página de releases no GitHub](https://github.com/anomalyco/libryno/releases)
2. Baixe o arquivo `LIBRYNO-Setup-2.0.0.exe`
3. Execute o instalador e siga as instruções

#### Linux
```bash
# Via instalador (Debian/Ubuntu)
wget https://github.com/anomalyco/libryno/releases/download/v2.0.0/libryno-2.0.0-linux-x64.deb
sudo dpkg -i libryno-2.0.0-linux-x64.deb
sudo apt install -f  # Corrige dependências

# Via AppImage (qualquer distribuição)
wget https://github.com/anomalyco/libryno/releases/download/v2.0.0/libryno-2.0.0-linux-x64.AppImage
chmod +x libryno-2.0.0-linux-x64.AppImage
./libryno-2.0.0-linux-x64.AppImage
```

### Opção 2: Via Git (Código Fonte)

```bash
# Clone o repositório
git clone https://github.com/anomalyco/libryno.git
cd libryno

# Instale as dependências
pip install -r requirements.txt

# Configure o ambiente
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Execute
python src/main.py
```

### Opção 3: Build Local

```bash
# Instale PyInstaller
pip install pyinstaller

# Build com PyInstaller
make build        # Linux
build.bat         # Windows

# O executável estará em dist/
```

### Requisitos

- Python 3.10+
- pip
- (Para build) PyInstaller 5.10+

## Estrutura do Projeto

```
src/
├── main.py              # Ponto de entrada
├── app.py               # Bootstrap do aplicativo
├── config.py            # Configurações
├── core/
│   ├── database.py      # SQLite + SQLAlchemy
│   ├── models.py        # Modelos de dados
│   └── migrations.py    # Setup do banco
├── auth/
│   ├── ordob_client.py  # Cliente API OrdoB (com retry + SSE)
│   ├── session.py       # Gerenciamento de sessão
│   └── license.py       # Validação de licença + monitoramento
├── features/
│   ├── books.py         # CRUD Livros
│   ├── readers.py       # CRUD Leitores
│   ├── collaborators.py # CRUD Colaboradores
│   ├── loans.py         # Empréstimos (PREMIUM)
│   ├── reports.py       # Relatórios PDF (PREMIUM)
│   ├── notifications.py # Notificações (PREMIUM)
│   ├── backup.py        # Backup (PREMIUM)
│   └── catalog.py       # Catalogação (PREMIUM)
├── ui/
│   ├── screens/         # Telas principais
│   ├── widgets/         # Componentes reutilizáveis
│   ├── themes/          # Temas visuais
│   └── i18n/            # Idiomas
└── utils/
    ├── sse_client.py    # Cliente SSE tempo real
    ├── logger.py        # Logging
    ├── crypto.py        # Hash de senhas
    ├── validators.py    # Validações
    ├── excel_export.py  # Exportação Excel
    ├── isbn_api.py      # Consulta ISBN
    └── ...
```

## Funcionalidades

### Tier FREE
- Login via OrdoB
- CRUD de Livros, Leitores e Colaboradores
- Dashboard com gráficos
- Busca global multi-tabela
- Exportação para Excel
- Consulta ISBN automática
- Tema escuro

### Tier PREMIUM (Chave OrdoB)
- Sistema de empréstimos com multas
- Relatórios avançados em PDF
- Multi-usuário com permissões
- Backup automático
- Notificações em tempo real
- Catalogação com tags e capas
- 5+ temas visuais
- Sem anúncios
- Suporte prioritário

## Temas

Ciclo de temas com botão na sidebar:
- **Dark** (padrão)
- **Light**

## Idiomas

- Português BR (padrão)
- Inglês

## Tecnologias

- **GUI**: PySide6 (Qt for Python)
- **Database**: SQLite via SQLAlchemy
- **Auth**: OrdoB Core API
- **Charts**: Matplotlib
- **PDF**: ReportLab
- **Excel**: Pandas + openpyxl
- **Build**: PyInstaller

## Licença

Apache License 2.0

---

Desenvolvido por **OrdoB** Nova Friburgo/RJ
