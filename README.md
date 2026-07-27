# LIBRYNO v2.0

Sistema de Gestão de Biblioteca Pública integrado ao ecossistema **OrdoB**.

## Instalação

### Requisitos
- Python 3.10+
- pip

### Setup

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/libryno.git
cd libryno

# Instale as dependências
pip install -r requirements.txt

# Configure o ambiente
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Execute
python src/main.py
```

### Build (Gerar Instalador)

```bash
# Instale PyInstaller
pip install pyinstaller

# Gere o executável
pyinstaller build.spec --clean

# O executável estará em dist/
```

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
│   ├── ordob_client.py  # Cliente API OrdoB
│   ├── session.py       # Gerenciamento de sessão
│   └── license.py       # Validação de licença
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
└── utils/               # Utilitários
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

- **GUI**: PyQt5
- **Database**: SQLite via SQLAlchemy
- **Auth**: OrdoB Core API
- **Charts**: Matplotlib
- **PDF**: ReportLab
- **Excel**: Pandas + openpyxl
- **Build**: PyInstaller

## Licença

Apache License 2.0

---

Desenvolvido por **Wesley Alves** para a Biblioteca Pública Municipal Maria Margarida Liguori - Nova Friburgo/RJ
