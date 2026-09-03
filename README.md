# LIBRYNO v2.0

Sistema de Gestão de Biblioteca integrado ao ecossistema **OrdoB**.

## ⚠️ Autenticação Obrigatória

**O Libryno SÓ funciona com autenticação via API OrdoB.**

Qualquer usuário que execute o aplicativo DEVE fazer login com uma conta OrdoB válida. Não existe modo offline ou acesso sem autenticação.

### Fluxo de autenticação

```
App inicia
    ↓
Sessão salva existe?
├── SIM → Validar token no servidor OrdoB
│         ├── Token válido → Liberar acesso
│         ├── Token expirado → Forçar re-login
│         └── API inacessível → Bloquear acesso + aviso
└── NÃO → Exibir tela de login OrdoB
```

### Regras de segurança

- Sessão local é protegida por assinatura HMAC-SHA256
- Sessão adulterada é automaticamente descartada
- Token é validado contra a API a cada hora
- Se token expirar, usuário é deslogado automaticamente

---

## Planos

### Tier FREE (gratuito)
- Login via OrdoB
- CRUD de Livros (até **50 livros**)
- CRUD de Leitores (até **50 leitores**)
- CRUD de Colaboradores (até **3 colaboradores**)
- Dashboard com gráficos
- Busca global multi-tabela
- Exportação para Excel (até **3/dia**)
- Consulta ISBN automática
- Tema escuro/claro

### Tier PREMIUM (Chave OrdoB)
- Tudo do FREE + **sem limites de registros**
- Sistema de empréstimos com multas
- Relatórios avançados em PDF
- Multi-usuário com permissões
- Backup automático
- Notificações em tempo real (SSE)
- Catalogação com tags e capas
- Importação de planilhas
- 5+ temas visuais
- Sem anúncios
- Suporte prioritário

### Limites do FREE tier

| Recurso | FREE | PREMIUM |
|---------|------|---------|
| Livros | 50 | Ilimitado |
| Leitores | 50 | Ilimitado |
| Colaboradores | 3 | Ilimitado |
| Exportações/dia | 3 | Ilimitado |
| Empréstimos | ❌ | ✅ |
| Relatórios PDF | ❌ | ✅ |
| Backup | ❌ | ✅ |
| Notificações SSE | ❌ | ✅ |
| Importação planilhas | ❌ | ✅ |

---

## Instalação

### Opção 1: Executável Pronto (Recomendado)

#### Windows
1. Acesse a [página de releases no GitHub](https://github.com/OrdoB/Libryno/releases)
2. Baixe o arquivo `Libryno-Setup.exe`
3. Execute o instalador e siga as instruções

#### Linux
```bash
# Via instalador (Debian/Ubuntu)
wget https://github.com/OrdoB/Libryno/releases/download/v2.0.0/libryno-linux-x64.deb
sudo dpkg -i libryno-linux-x64.deb
sudo apt install -f

# Via AppImage (qualquer distribuição)
wget https://github.com/OrdoB/Libryno/releases/download/v2.0.0/libryno-linux-x64.AppImage
chmod +x libryno-linux-x64.AppImage
./libryno-linux-x64.AppImage
```

### Opção 2: Via Git (Código Fonte)

```bash
git clone https://github.com/OrdoB/Libryno.git
cd LIBRYNO
pip install -r requirements.txt
cp .env.example .env
python src/main.py
```

### Opção 3: Build Local

```bash
pip install pyinstaller
make build        # Linux
build.bat         # Windows
```

### Requisitos

- Python 3.10+
- pip
- (Para build) PyInstaller 5.10+

---

## Estrutura do Projeto

```
src/
├── main.py              # Ponto de entrada
├── app.py               # Bootstrap + auth enforcement
├── config.py            # Configurações
├── core/
│   ├── database.py      # SQLite + SQLAlchemy
│   ├── models.py        # Modelos de dados
│   ├── migrations.py    # Setup do banco
│   └── seed.py          # Dados demo (após auth)
├── auth/
│   ├── ordob_client.py  # Cliente API OrdoB (retry + SSE)
│   ├── session.py       # Sessão com HMAC anti-tampering
│   └── license.py       # Validação licença + token
├── features/
│   ├── books.py         # CRUD Livros (com FREE tier check)
│   ├── readers.py       # CRUD Leitores (com FREE tier check)
│   ├── collaborators.py # CRUD Colaboradores
│   ├── loans.py         # Empréstimos (PREMIUM)
│   ├── reports.py       # Relatórios PDF (PREMIUM)
│   ├── notifications.py # Notificações (PREMIUM)
│   ├── backup.py        # Backup (PREMIUM)
│   ├── catalog.py       # Catalogação (PREMIUM)
│   └── import_data.py   # Importação de planilhas
├── sync/
│   └── sync_manager.py  # Sincronização bidirecional
├── ui/
│   ├── screens/
│   │   ├── login.py     # Tela de login OrdoB
│   │   └── home.py      # Dashboard + CRUD
│   ├── widgets/
│   │   ├── premium_badge.py
│   │   └── toast.py
│   ├── themes/
│   │   ├── dark.qss
│   │   ├── light.qss
│   │   └── theme_manager.py
│   └── i18n/
│       ├── pt_BR.json
│       ├── en.json
│       └── translator.py
└── utils/
    ├── constants.py     # Constantes + limites FREE/PREMIUM
    ├── crypto.py        # bcrypt
    ├── excel_export.py
    ├── isbn_api.py
    ├── logger.py        # loguru
    ├── sse_client.py
    ├── system_theme.py
    └── validators.py
```

---

## Tecnologias

- **GUI**: PySide6 (Qt for Python)
- **Database**: SQLite via SQLAlchemy
- **Auth**: OrdoB Core API (SSO obrigatório)
- **Charts**: Matplotlib
- **PDF**: ReportLab
- **Excel**: Pandas + openpyxl
- **Build**: PyInstaller
- **Security**: bcrypt + HMAC-SHA256 session signing

## Licença

Apache License 2.0

---

Desenvolvido por **OrdoB**
