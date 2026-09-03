# Libryno

[![Libryno](https://img.shields.io/badge/Libryno-v2.0-5CE1E6?style=for-the-badge&logo=python&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![PySide6](https://img.shields.io/badge/PySide6-6.5+-41CD52?style=for-the-badge&logo=qt&logoColor=white)](#)

Sistema Desktop e robusto de **Gestão de Biblioteca Pública**, desenvolvido nativamente em Python com uma GUI moderna e integrado perfeitamente ao ecossistema cloud **OrdoB**.

## 🚀 Destaques do Projeto (Para Recrutadores e Engenheiros)

O **Libryno** demonstra versatilidade e o uso eficiente de aplicações nativas Desktop comunicando-se com serviços em nuvem. 

- **Autenticação Híbrida (Desktop/Cloud):** Utiliza um fluxo rigoroso de checagem. A aplicação local valida a sessão do usuário via API RESTful do *OrdoB Core*. A integridade dos dados locais do usuário ativo é validada utilizando assinaturas **HMAC-SHA256**.
- **Modelagem Relacional Offline-First:** Usa SQLite (local) orquestrado pelo poderoso **SQLAlchemy** (ORM). Traz excelente performance de I/O em máquinas limitadas típicas de organizações públicas.
- **Integração de APIs Acessórias:** Faz comunicação externa para captura de metadados literários via *Consulta de ISBN Automática* e integra geração rica de arquivos, transformando base de dados em relatórios PDF e exportações Excel (Pandas + ReportLab).
- **Interface Gráfica Nativa (GUI):** Desenvolvido utilizando o robusto PySide6 (bindings oficiais do framework Qt), oferecendo uma interface reativa, assíncrona, multithread e visualmente polida (Dark/Light themes).

## 🛠️ Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| **GUI** | PySide6 (Qt for Python) |
| **Database** | SQLite + SQLAlchemy (ORM) |
| **SSO & Licença**| OrdoB Core API (via Requests) |
| **Data Eng.** | Matplotlib (Charts) + Pandas (Excel) |
| **Build & Deploy**| PyInstaller |
| **Segurança** | bcrypt (Criptografia local), HMAC-SHA256 (Anti-tampering) |

## 📦 Estrutura e Features

- **Tiers de Acesso dinâmico:** Controle por chaves no backend (FREE tier possui limitação de inserts mapeada e tratada graciosamente na GUI, PREMIUM ativa logs de relatórios completos e destrava bloqueios).
- **Empréstimos, Leitores e Livros:** Controle rigoroso de estoque literário, tracking de empréstimos, retornos e geração automatizada de multas por atraso.
- **Notificações Realtime (SSE):** O Desktop consegue receber e disparar notificações assíncronas do backend remoto utilizando *Server-Sent Events*.

## 🔧 Executando a partir da Fonte

Requisitos: Python 3.10+
```bash
git clone https://github.com/ordo-b/LIBRYNO.git
cd LIBRYNO
pip install -r requirements.txt
cp .env.example .env
python src/main.py
```
*(Testes inclusos, rode via `pytest`)*

---
*Parte do portfólio de engenharia OrdoB: prova competência no universo Python, Qt e integrações Desktop-Cloud.*