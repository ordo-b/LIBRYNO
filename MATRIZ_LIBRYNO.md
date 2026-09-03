# Libryno — Matriz Mestra do Produto (Single Source of Truth)

> **Base principal:** `PLANOLIBRYNO.md` (visão completa do sistema)  
> **Consolidado em:** 02/09/2026  
> **Versão:** 2.0.0  
> **Status:** 🟢 **Core Produção-ready** + 🟡 **Funcionalidades Premium + Packaging pendentes**

---

## 1. VISÃO GERAL DO PRODUTO

### 1.1 Definição Oficial

**Libryno** é um sistema de gestão de bibliotecas públicas integrado ao ecossistema OrdoB, desenvolvido em Python com interface gráfica PySide6 (Qt for Python). O sistema SÓ funciona com autenticação via API OrdoB — não existe modo offline. Todo usuário deve fazer login com uma conta OrdoB válida para usar o sistema.

### 1.2 Posicionamento no Ecossistema OrdoB

```
                    ORDOB CORE
                        │
               IDENTIDADE / TENANT / LICENÇA
                        │
                    ┌─────┴─────┐
                    │           │
                  FLUX        LOOM
                    │           │
               ESTOQUE/WMS  CONFECÇÃO
                    │           │
                    └─────┬─────┘
                          │
                     LIBRYNO
                          │
                    BIBLIOTECA PÚBLICA
```

**Princípio:** Libryno é um **produto filho do OrdoB** que consome:
- **Autenticação/SSO** via OrdoB Core (JWT + SSE)
- **Licenciamento** via OrdoB Core (validação de plano + features)
- **Organização/Empresa** via OrdoB Core (escopo por org_id)

---

## 2. ARQUITETURA TÉCNICA ATUAL

### 2.1 Stack Tecnológica

| Camada | Tecnologia | Versão | Status |
|--------|------------|--------|--------|
| **GUI** | PySide6 (Qt for Python) | ≥6.5 | ✅ |
| **Banco** | SQLite + SQLAlchemy | ≥2.0 | ✅ |
| **Auth/SSO** | OrdoB Core API | - | ✅ |
| **Charts** | Matplotlib | ≥3.9 | ✅ |
| **PDF** | ReportLab | ≥4.0 | ✅ |
| **Excel** | Pandas + openpyxl | ≥2.2 | ✅ |
| **Build** | PyInstaller | ≥5.10 | ✅ |
| **Logging** | Loguru | ≥0.7 | ✅ |
| **Password** | bcrypt | ≥4.0 | ✅ |
| **HTTP/SSE** | requests + requests-sse | ≥2.32 | ✅ |

### 2.2 Estrutura de Pastas (Monorepo)

```
libryno/
├── src/
│   ├── main.py              # Ponto de entrada
│   ├── app.py               # Bootstrap + auth enforcement
│   ├── config.py            # Configurações centralizadas
│   ├── auth/                # Autenticação OrdoB
│   │   ├── ordob_client.py  # Cliente API com retry + SSE
│   │   ├── session.py       # Sessão com HMAC anti-tampering
│   │   └── license.py       # Validação de licença + token
│   ├── core/                # Core do sistema
│   │   ├── database.py      # SQLite + SQLAlchemy
│   │   ├── models.py        # Modelos de dados (ORM)
│   │   ├── migrations.py    # Setup do banco
│   │   └── seed.py          # Dados de demonstração
│   ├── features/            # Funcionalidades
│   │   ├── books.py         # CRUD Livros (FREE tier check)
│   │   ├── readers.py       # CRUD Leitores (FREE tier check)
│   │   ├── collaborators.py # CRUD Colaboradores
│   │   ├── loans.py         # Empréstimos (PREMIUM)
│   │   ├── reports.py       # Relatórios PDF (PREMIUM)
│   │   ├── notifications.py # Notificações (PREMIUM)
│   │   ├── backup.py        # Backup (PREMIUM)
│   │   ├── catalog.py       # Catalogação (PREMIUM)
│   │   └── import_data.py   # Importação de planilhas
│   ├── sync/                # Sincronização
│   │   └── sync_manager.py  # Gerenciador de sync
│   ├── ui/                  # Interface gráfica
│   │   ├── screens/         # Telas principais
│   │   │   ├── login.py     # Tela de login
│   │   │   └── home.py      # Tela principal (Dashboard)
│   │   ├── widgets/         # Componentes reutilizáveis
│   │   ├── themes/          # Temas visuais
│   │   └── i18n/            # Idiomas
│   └── utils/               # Utilitários
│       ├── constants.py     # Constantes + limites FREE/PREMIUM
│       ├── crypto.py        # Hash de senhas (bcrypt)
│       ├── excel_export.py  # Exportação Excel
│       ├── isbn_api.py      # Consulta ISBN
│       ├── logger.py        # Logging (loguru)
│       ├── sse_client.py    # Cliente SSE tempo real
│       └── validators.py    # Validações
├── tests/                   # Testes
├── packaging/               # Build scripts
├── data/                    # Dados (banco, assets)
├── img/                     # Assets visuais
└── packaging/               # PyInstaller specs
```

---

## 3. MODELO DE DADOS (SQLAlchemy + SQLite)

### 3.1 Tabelas Core

| Tabela | Descrição | Status |
|--------|-----------|--------|
| `users` | Usuário logado + licença + org | ✅ |
| `books` | Livros (tombo, ISBN, autor, etc.) | ✅ |
| `readers` | Leitores (CPF, endereço, etc.) | ✅ |
| `collaborators` | Colaboradores (usuários internos) | ✅ |
| `loans` | Empréstimos (PREMIUM) | ✅ |
| `notifications` | Notificações | ✅ |
| `backup_records` | Histórico de backups | ✅ |

### 3.2 Relacionamentos

```
User (1) ─────< Book
User (1) ─────< Reader
User (1) ─────< Collaborator
Book (1) ─────< Loan >───── (1) Reader
Collaborator (1) ─────< Loan
```

### 3.3 Limites FREE vs PREMIUM

| Recurso | FREE | PREMIUM |
|---------|------|---------|
| Livros | 50 | Ilimitado |
| Leitores | 50 | Ilimitado |
| Colaboradores | 3 | Ilimitado |
| Empréstimos | ❌ | ✅ |
| Relatórios PDF | ❌ | ✅ |
| Backup Auto | ❌ | ✅ |
| Notificações SSE | ❌ | ✅ |
| Catalogação (tags/capas) | ❌ | ✅ |
| Importação Planilhas | ❌ | ✅ |
| Temas Visuais | 1 | 5+ |
| Exportação Excel | 3/dia | Ilimitado |

---

## 4. FUNCIONALIDADES IMPLEMENTADAS

### 4.1 Autenticação & SSO OrdoB ✅
- `login.py`: Tela de login com validação server-side
- `ordob_client.py`: Cliente HTTP com retry exponencial + health check
- `session.py`: Sessão local com HMAC anti-tampering + persistência QSettings
- `license.py`: Validação de licença + detecção automática premium + monitoramento periódico
- SSE: Stream de notificações tempo real via `sse_client.py`
- Login via navegador (browser OAuth) como alternativa

### 4.2 CRUD Livros (books.py) ✅
- CRUD completo: create, read_all, update, delete, search, count
- Busca multi-campo (título, autor, ISBN, tombo, classificação, editora, assunto)
- Validação `validate_book` + FREE tier limit (50 livros)
- ISBN automático via API (Google Books/OpenLibrary)

### 4.3 CRUD Leitores (readers.py) ✅
- CRUD completo com validação CPF/CEP/email
- FREE tier limit (50 leitores)

### 4.4 CRUD Colaboradores (collaborators.py) ✅
- CRUD com bcrypt password hashing
- Roles: admin, manager, librarian, collaborator
- FREE tier limit (3 colaboradores)

### 4.5 Empréstimos (loans.py) 🟡 PREMIUM
- CRUD empréstimos com multa automática
- Status: active, returned, overdue
- Multa por dia configurável por tipo de leitor
- **Pendente:** Renovações, reservas, bloqueio por multa

### 4.4 Dashboard (home.py) ✅
- Sidebar com navegação por abas
- Gráficos Matplotlib (empréstimos por mês, categorias, top leitores)
- Stats cards: total livros, leitores ativos, empréstimos ativos, atrasados
- Tabs: Livros, Leitores, Colaboradores, Empréstimos, Relatórios, Configurações

### 4.5 Relatórios (reports.py) 🟡 PREMIUM
- PDF: Livros, Leitores, Empréstimos, Financeiro
- **Pendente:** Relatórios customizáveis, agendamento

### 4.6 Importação de Dados (import_data.py) 🟡 PREMIUM
- Importação de planilhas (books, readers)
- Template Excel/CSV
- Validação em lote

### 4.7 Backup (backup.py) 🟡 PREMIUM
- Backup completo (JSON + media opcional)
- **Pendente:** Agendamento automático, compressão, restore guiado

### 4.8 Catalogação (catalog.py) 🟡 PREMIUM
- Tags, capas, sinopse
- **Pendente:** Categorias hierárquicas, avaliações, listas de leitura

### 4.7 Notificações (notifications.py) 🟡 PREMIUM
- CRUD + SSE tempo real
- **Pendente:** Email/SMS/Push, templates, agendamento

---

## 5. AUTENTICAÇÃO & LICENCIAMENTO

### 5.1 Fluxo de Login
```
1. Usuário abre Libryno → tela de login
2. Digita email/senha OR clica "Login via Navegador" (OAuth OrdoB)
3. Envia email/senha para api.ordob.com/v1/auth/login
4. Se válido → recebe JWT + user data + licenses
5. Salva sessão local (HMAC + QSettings)
6. Verifica licença ativa para produto "libryno"
6. Carrega HomeScreen ou redireciona para /cadastro
```

### 5.2 Validação de Licença (LicenseManager)
- **Validação inicial:** `validate_license(license_key)` → POST /v1/license/validate
- **Detecção automática:** `auto_detect_premium()` após login → GET /v1/licenses
- **Verificação periódica:** Cada 1h (token + licença) em background thread
- **Expiração:** Downgrade automático para FREE + notificação

### 5.3 Tier Features (constants.py)

```python
FREE_MAX_BOOKS = 50
FREE_MAX_READERS = 50
FREE_MAX_COLLABS = 3
FREE_MAX_EXPORTS_DAY = 3
FREE_MAX_IMPORTS = 0
FREE_THEMES = 1
PREMIUM_THEMES = 5
```

---

## 6. PACKAGING & DISTRIBUIÇÃO (PyInstaller)

### 6.1 Scripts de Build Existentes

| Arquivo | Descrição |
|---------|-----------|
| `build.spec` | Spec PyInstaller (Linux/Windows) |
| `build.sh` | Script Linux (chmod +x) |
| `build.bat` | Script Windows |
| `Makefile` | Comandos utilitários |

### 6.2 Build.spec Atual (Análise)

O `build.spec` inclui:
- ✅ Hidden imports (PySide6, sqlalchemy, matplotlib, reportlab, pandas, etc.)
- ✅ Datas: `img/`, `data/`, `src/ui/themes/`, `src/ui/i18n/`
- ✅ Binaries: matplotlib backends
- ⚠️ **Pendente:** Assinatura de código (code signing Windows)
- ⚠️ **Pendente:** Atualizador automático
- ⚠️ **Pendente:** Instalador MSI/NSIS profissional

### 6.3 Artefatos de Build Esperados

| Plataforma | Artefato | Status |
|------------|----------|--------|
| Windows | `Libryno-Setup.exe` (NSIS) | ❌ |
| Windows | `Libryno-Portable.exe` | ⚠️ (build direto .exe) |
| Linux | `Libryno-<version>-x86_64.AppImage` | ⚠️ |
| Linux | `libryno-<version>-amd64.deb` | ❌ |
| macOS | `Libryno-<version>.dmg` | ❌ |

---

## 7. DOCUMENTAÇÃO EXISTENTE

| Arquivo | Propósito | Status |
|---------|-----------|--------|
| `PLANOLIBRYNO.md` | Plano mestre completo (10 fases) | ✅ Base histórica |
| `README.md` | Visão geral + instalação + badges | ✅ |
| `api-ordob.md` | Documentação API OrdoB integração | ✅ |
| `requirements.txt` | Dependências runtime | ✅ |
| `requirements-dev.txt` | Dependências dev | ✅ |
| `.env.example` | Template config | ✅ |
| `LICENSE` | Apache 2.0 | ✅ |

---

## 8. GAPS PARA PRODUÇÃO / DOWNLOAD NO SITE OFICIAL

### 8.1 Críticos (Bloqueiam Release)

| Item | Descrição | Prioridade |
|------|-----------|------------|
| **Installer Windows (NSIS/MSI)** | `.exe` instalável com assinatura digital | 🔴 Crítica |
| **Code Signing (Windows)** | Certificado EV para evitar SmartScreen | 🔴 Crítica |
| **Atualizador Automático** | Verificação + download + apply no startup | 🔴 Crítica |
| **Tratamento de Erro Robusto** | Try/catch global, logs de crash, relatório ao OrdoB | 🔴 Crítica |
| **Testes Automatizados** | pytest > 80% coverage (unit + integration) | 🔴 Crítica |

### 8.2 Altos (Necessários para Qualidade)

| Item | Descrição | Prioridade |
|------|-----------|------------|
| **AppImage Linux** | Build automatizado + teste CI | 🟠 Alta |
| **DMG macOS** | Build + notarização Apple | 🟠 Alta |
| **Deb/RPM Linux** | Pacotes nativos | 🟠 Alta |
| **Atualizador Diferencial** | Delta updates (bsdiff) | 🟠 Alta |
| **Telemetria Ópt-in** | Crash reports + uso anônimo | 🟠 Alta |
| **Multi-Biblioteca (Rede)** | Modelo Library + isolamento por org | 🟠 Alta |
| **Modo Offline Completo** | Queue local + sync quando online | 🟠 Alta |
| **App Mobile (Flutter)** | Leitura catálogo + empréstimos | 🟠 Alta |

### 8.3 Melhorias UX/UI (Fase 7 do Plano)

| Item | Descrição |
|------|-----------|
| **Design System Completo** | Botões, Cards, Tables, Forms, Modals, Toasts padronizados |
| **Temas Visuais (5+)** | Dark, Light, Sepia, High Contrast, Custom |
| **Acessibilidade WCAG 2.1 AA** | Contraste, navegação teclado, screen readers |
| **Responsividade** | Breakpoints mobile/tablet/desktop |
| **Animações/Micro-interações** | Transições suaves, feedback visual |
| **Onboarding** | Tour guiado primeiro acesso |
| **Busca Global (Ctrl+K)** | Busca fuzzy em tudo |

### 8.4 Funcionalidades Premium Pendentes (Fases 3-6)

| Fase | Funcionalidade | Status |
|------|----------------|--------|
| 3 | Empréstimos: renovações, reservas, bloqueio multa | 🟡 Parcial |
| 3 | Multas: pagamento, relatórios, bloqueio | 🟡 Parcial |
| 4 | Relatórios customizáveis + agendamento | ❌ Ausente |
| 4 | Dashboard analytics avançado (heatmap, treemap) | ❌ Ausente |
| 5 | Catalogação: categorias hierárquicas, avaliações | ❌ Ausente |
| 5 | Notificações: email/SMS/push + templates | ❌ Ausente |
| 5 | Backup: agendamento, compressão, restore guiado | ❌ Ausente |
| 6 | Modo offline completo (queue + sync) | ❌ Ausente |
| 6 | Sync avançada (conflitos, delta) | ❌ Ausente |
| 6 | Multi-biblioteca (rede) | ❌ Ausente |

---

## 9. INTEGRAÇÃO COM ECOSSISTEMA ORDOB

### 9.1 Endpoints Consumidos

| Endpoint | Uso | Status |
|----------|-----|--------|
| `POST /v1/auth/login` | Login email/senha | ✅ |
| `POST /v1/auth/register` | Registro conta | ✅ |
| `GET /v1/user` | Dados usuário | ✅ |
| `POST /v1/auth/logout` | Logout | ✅ |
| `POST /v1/license/validate` | Valida licença | ✅ |
| `GET /v1/licenses` | Lista licenças | ✅ |
| `GET /health` | Health check | ✅ |
| `GET /api/v1/notifications/stream` | SSE notifications | ✅ |
| `POST /v1/tickets` | Suporte | ✅ |

### 9.2 Fluxo de Acesso ao Produto (OrdoB Core → Libryno)

```
Usuário logado no ordob.com
    ↓
Clica em "Acessar" na licença Libryno
    ↓
ordob.com redireciona: https://libryno.ordob.com?token=xxx&organization_id=yyy&license_id=zzz
    ↓
Libryno recebe token + org_id + license_id
    ↓
Valida token + licença via API OrdoB
    ↓
Cria sessão local + carrega HomeScreen
```

---

## 10. TESTES & QUALIDADE

### 9.1 Estrutura Atual

```
tests/
├── unit/           # ✅ Parcial (auth, models)
├── integration/    # ❌ Ausente
├── ui/             # ❌ Ausente
└── fixtures/       # ⚠️ Parcial
```

### 9.2 Meta de Cobertura

| Tipo | Meta | Atual |
|------|------|-------|
| Unitários | 90% | ~30% |
| Integração | 70% | 0% |
| UI | 60% | 0% |

---

## 10. CI/CD & DEPLOY

### 10.1 Pipeline Necessário (GitHub Actions)

```yaml
stages:
  - lint: ruff check + ruff format --check
  - test: pytest --cov=src --cov-report=xml (target >80%)
  - build: 
      - Windows: pyinstaller + NSIS installer + code sign
      - Linux: pyinstaller + AppImage + .deb
      - macOS: pyinstaller + .dmg + notarize
  - deploy:
      - GitHub Release (artifacts)
      - Site oficial (download page update)
      - Auto-update manifest (version.json)
```

### 10.2 Site Oficial (ordob.com/libryno)

| Item | Status |
|------|--------|
| Landing Page | ⚠️ Parcial (existe em /produtos/libryno) |
| Página de Download | ❌ Ausente |
| Auto-update Manifest | ❌ Ausente |
| Changelog Público | ❌ Ausente |
| Documentação Usuário | ❌ Ausente |
| FAQ / Suporte | ❌ Ausente |

---

## 11. ROADMAP CONSOLIDADO (Baseado no PLANOLIBRYNO.md)

### ✅ FASE 0 — Auditoria (Concluída)
- Mapeamento técnico completo
- Matriz Existe/Melhorar/Criar

### ✅ FASE 1 — Fundação (Concluída)
- Estrutura multi-biblioteca (parcial - modelo User apenas)
- Usuários/permissões (básico)
- Segurança/isolamento (HMAC + org_id)

### ✅ FASE 2 — Cadastro Mestre (Concluída)
- Livros, Leitores, Colaboradores (básico + FREE limits)
- ISBN automático
- **Pendente:** Campos avançados (edição, páginas, idioma, gênero, condição, localização física, categorias/tags)

### 🟡 FASE 3 — Empréstimos Avançados (Em Andamento)
- ✅ CRUD básico + multa automática
- ❌ Renovações, reservas, bloqueio por multa
- ❌ Pagamento de multas + relatórios

### 🟡 FASE 4 — Relatórios & Analytics (Parcial)
- ✅ PDF básicos (livros, leitores, empréstimos, financeiro)
- ❌ Customizáveis, agendamento, dashboard analytics avançado

### ❌ FASE 5 — Premium Features (Não Iniciado)
- Catalogação avançada (categorias hierárquicas, tags, capas, avaliações)
- Notificações inteligentes (email/SMS/push + templates)
- Backup avançado (agendamento, compressão, restore guiado)
- Modo offline completo (queue + sync)

### ❌ FASE 6 — Integração OrdoB (Parcial)
- ✅ SSO, licença, SSE
- ❌ Sync tempo real completa (conflitos, delta)
- ❌ Multi-biblioteca (rede)

### ❌ FASE 7 — UX/UI (Não Iniciado)
- Design system, temas, acessibilidade, onboarding, animações

### ❌ FASE 8 — Testes (Não Iniciado)
- Unit, Integration, UI tests + CI/CD

### ❌ FASE 9 — Performance (Não Iniciado)
- Índices, pagination, virtual scroll, cache

### ❌ FASE 10 — Roadmap Futuro
- v2.1: UX, temas, relatórios custom, backup auto
- v2.2: Offline, sync, mobile, integrações
- v3.0: IA recomendações, chatbot, preditiva, multi-biblio
- v4.0: Marketplace, empréstimo interbibliotecas, AR, IoT

---

## 11. ARQUIVOS DE REFERÊNCIA (Mantidos)

| Arquivo | Propósito | Manter? |
|---------|-----------|---------|
| `MATRIZ_LIBRYNO.md` | **Este documento — Single Source of Truth** | ✅ **SIM** |
| `README.md` | Visão geral pública (GitHub) | ✅ SIM |
| `PLANOLIBRYNO.md` | Plano mestre detalhado (histórico) | ✅ SIM (referência) |
| `api-ordob.md` | Doc API integração | ✅ SIM |
| `requirements.txt` / `-dev.txt` | Dependências | ✅ SIM |
| `.env.example` | Template config | ✅ SIM |
| `LICENSE` | Apache 2.0 | ✅ SIM |

---

## 12. PRÓXIMAS AÇÕES IMEDIATAS (Sprint Atual)

| # | Ação | Responsável | Prazo |
|---|------|-------------|-------|
| 1 | **Installer Windows NSIS + Code Signing** | DevOps | Semana 1 |
| 2 | **Auto-updater (check + download + apply)** | Backend | Semana 1 |
| 3 | **Error Boundary Global + Crash Reporter** | Frontend | Semana 1 |
| 4 | **Testes Unitários (pytest + coverage > 80%)** | QA/Backend | Semana 2 |
| 5 | **CI/CD GitHub Actions (build + test + deploy)** | DevOps | Semana 2 |
| 6 | **AppImage Linux + .deb** | DevOps | Semana 2 |
| 7 | **Campos Avançados Livros/Leitores** | Backend | Semana 3 |
| 8 | **Empréstimos: Renovações + Reservas** | Backend | Semana 3 |
| 9 | **Design System + Temas (5+)** | Frontend | Semana 3 |
| 10 | **Site Oficial: Página Download + Auto-update Manifest** | DevOps | Semana 4 |

---

## 13. COMANDOS ÚTEIS DE DESENVOLVIMENTO

```bash
# Desenvolvimento
cd LIBRYNO
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
python src/main.py

# Testes
pytest -v
pytest --cov=src --cov-report=html

# Lint/Format
ruff check src/
ruff format src/

# Build
# Windows
build.bat
# Linux
./build.sh

# PyInstaller direto
pyinstaller build.spec
```

---

## 14. CONTATO & LINKS

- **Produção (Site Oficial):** https://ordob.com/libryno
- **GitHub:** https://github.com/ordo-b/LIBRYNO
- **OrdoB Core:** https://ordob.com
- **Suporte:** https://ordob.com/suporte
- **Releases:** https://github.com/ordo-b/LIBRYNO/releases

---

## 15. ARQUIVOS REMOVIDOS (Consolidados)

Os seguintes arquivos foram **consolidados nesta matriz** e podem ser removidos se redundantes:

| Arquivo | Motivo |
|---------|--------|
| `PLANOLIBRYNO.md` | Mantido como referência histórica, conteúdo consolidado aqui |

---

## LEGENDA DE STATUS

| Símbolo | Significado |
|---------|-------------|
| ✅ | **Implementado e testado** |
| 🟡 | **Parcial / Em andamento** |
| ❌ | **Não iniciado / Ausente** |
| 🔴 | **Crítico (bloqueia release)** |
| 🟠 | **Alto (necessário para qualidade)** |
| ⚠️ | **Parcial / Precisa atenção** |

---

> **Nota:** Este documento substitui a necessidade de consultar múltiplos arquivos dispersos. `PLANOLIBRYNO.md` mantido como referência histórica da visão completa do produto. Para desenvolvimento ativo, usar **este documento (MATRIZ_LIBRYNO.md)** como referência única.