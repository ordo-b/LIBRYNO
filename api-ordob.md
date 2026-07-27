# OrdoB API — Documentação Oficial

> **Base URL:** `https://api.ordob.com/api` (produção)  
> **Base URL:** `http://localhost:8000/api` (desenvolvimento)  
> **Versão:** `v1`  
> **Formato:** JSON  
> **Autenticação:** Bearer Token (Laravel Sanctum)

---

## Índice

- [Autenticação](#autenticação)
- [Health Check](#health-check)
- [Auth](#auth)
- [User / Perfil](#user--perfil)
- [Produtos](#produtos)
- [Planos](#planos)
- [Licenças](#licenças)
- [Organizações](#organizações)
- [Pagamentos](#pagamentos)
- [Notificações](#notificações)
- [Tickets de Suporte](#tickets-de-suporte)
- [Webhooks (Asaas)](#webhooks-asaas)
- [Erros](#erros)
- [Modelos / Schemas](#modelos--schemas)

---

## Autenticação

Todas as rotas protegidas exigem o header:

```
Authorization: Bearer {token}
```

O token é obtido via `POST /api/v1/auth/login` ou `POST /api/v1/auth/register`.

<details>
<summary><b>Headers padrão</b></summary>

```http
Accept: application/json
Content-Type: application/json
Authorization: Bearer {token}  // apenas para rotas autenticadas
```
</details>

---

## Health Check

### `GET /api/health`

Verifica se a API está online.

**Resposta 200:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "name": "OrdoB Core API"
}
```

---

## Auth

### `POST /api/v1/auth/register`

Cria uma nova conta.

**Body:**
```json
{
  "name": "João Silva",
  "email": "joao@exemplo.com",
  "password": "MinhaSenha123!",
  "phone": "(11) 99999-9999",
  "company_name": "Minha Empresa Ltda",
  "document": "12.345.678/0001-90"
}
```

**Resposta 201:**
```json
{
  "message": "Conta criada com sucesso!",
  "user": {
    "id": 1,
    "uuid": "USR-A1B2C3",
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "phone": "(11) 99999-9999",
    "role": "user",
    "current_organization_id": 1,
    "created_at": "2026-07-27T10:00:00.000000Z"
  },
  "token": "1|abc123def456..."
}
```

---

### `POST /api/v1/auth/login`

Autentica um usuário existente.

**Body:**
```json
{
  "email": "joao@exemplo.com",
  "password": "MinhaSenha123!"
}
```

**Resposta 200:**
```json
{
  "message": "Login realizado com sucesso!",
  "user": {
    "id": 1,
    "uuid": "USR-A1B2C3",
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "role": "user"
  },
  "token": "1|abc123def456..."
}
```

**Resposta 401:**
```json
{
  "message": "Email ou senha inválidos."
}
```

---

### `GET /api/v1/auth/google`

Redireciona para a página de autenticação do Google.

> **Nota:** Rota de redirect — não retorna JSON.

---

### `GET /api/v1/auth/google/callback`

Callback do Google OAuth. Redireciona para o frontend com o token na URL.

> **Redirect:** `{frontend_url}/login?token={token}`

---

### `POST /api/v1/auth/forgot-password`

Solicita recuperação de senha.

**Body:**
```json
{
  "email": "joao@exemplo.com"
}
```

**Resposta 200:**
```json
{
  "message": "Se o email existir, você receberá um link de recuperação."
}
```

---

### `POST /api/v1/auth/reset-password`

Redefine a senha.

**Body:**
```json
{
  "token": "reset-token-aqui",
  "email": "joao@exemplo.com",
  "password": "NovaSenha123!"
}
```

**Resposta 200:**
```json
{
  "message": "Senha redefinida com sucesso!"
}
```

---

### `POST /api/v1/auth/logout`

> 🔒 Autenticado

Invalida o token atual.

**Resposta 200:**
```json
{
  "message": "Logout realizado com sucesso!"
}
```

---

## User / Perfil

### `GET /api/v1/user`

> 🔒 Autenticado

Retorna os dados do usuário logado com suas organizações.

**Resposta 200:**
```json
{
  "user": {
    "id": 1,
    "uuid": "USR-A1B2C3",
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "phone": "(11) 99999-9999",
    "role": "user",
    "avatar": null,
    "created_at": "2026-07-27T10:00:00.000000Z",
    "organizations": [
      {
        "id": 1,
        "name": "Minha Empresa Ltda",
        "pivot": { "role": "owner" }
      }
    ]
  }
}
```

---

### `PUT /api/v1/user`

> 🔒 Autenticado

Atualiza dados do perfil.

**Body:**
```json
{
  "name": "João Silva Atualizado",
  "phone": "(11) 98888-8888"
}
```

**Resposta 200:**
```json
{
  "message": "Perfil atualizado com sucesso!",
  "user": { ... }
}
```

---

### `PUT /api/v1/user/password`

> 🔒 Autenticado

Altera a senha do usuário.

**Body:**
```json
{
  "current_password": "MinhaSenha123!",
  "password": "NovaSenha456!",
  "password_confirmation": "NovaSenha456!"
}
```

**Resposta 200:**
```json
{
  "message": "Senha alterada com sucesso!"
}
```

---

## Produtos

### `GET /api/v1/products`

> Público

Lista todos os produtos ativos com seus planos.

**Resposta 200:**
```json
{
  "products": [
    {
      "id": 1,
      "name": "OrdoB Estoque",
      "slug": "estoque",
      "description": "Sistema inteligente de controle de estoque com IA preditiva.",
      "tagline": "Controle de estoque com inteligência artificial",
      "icon": "package",
      "color": "#3B82F6",
      "is_active": true,
      "plans": [
        {
          "id": 1,
          "name": "Starter",
          "price": 29.90,
          "description": "Para pequenos negócios",
          "features": ["Até 500 itens", "1 usuário", "Relatórios básicos"],
          "is_highlighted": false
        }
      ]
    }
  ]
}
```

---

### `GET /api/v1/products/{slug}`

> Público

Retorna um produto específico pelo slug.

**Exemplo:** `GET /api/v1/products/estoque`

**Resposta 200:**
```json
{
  "product": { ... }
}
```

**Resposta 404:**
```json
{
  "error": "Produto não encontrado."
}
```

---

## Planos

### `GET /api/v1/plans`

> Público

Lista todos os planos ativos.

**Resposta 200:**
```json
{
  "plans": [
    {
      "id": 1,
      "name": "Starter",
      "price": 29.90,
      "description": "Para pequenos negócios",
      "features": ["Até 500 itens"],
      "is_highlighted": false,
      "product": { "id": 1, "name": "OrdoB Estoque", "slug": "estoque" }
    }
  ]
}
```

---

### `GET /api/v1/plans/{product}`

> Público

Lista planos de um produto específico pelo slug.

**Resposta 200:**
```json
{
  "product": "OrdoB Estoque",
  "plans": [ ... ]
}
```

---

## Licenças

### `POST /api/v1/license/validate`

> Público (chamado por produtos SaaS)

Valida uma chave de licença.

**Body:**
```json
{
  "license_key": "ORDOB-EST-A1B2C",
  "product": "estoque"
}
```

**Resposta 200 (válida):**
```json
{
  "valid": true,
  "role": "owner",
  "organization": "Minha Empresa Ltda",
  "user": "João Silva",
  "access_token": "eyJsaWNlbnNlIjoiT1JET0ItRVNULU..."
}
```

**Resposta 200 (expirada):**
```json
{
  "valid": false,
  "error": "Licença expirada.",
  "expires_at": "2026-06-27T10:00:00.000000Z"
}
```

---

### `GET /api/v1/licenses`

> 🔒 Autenticado

Lista licenças do usuário logado.

**Resposta 200:**
```json
{
  "licenses": [
    {
      "id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "license_key": "ORDOB-EST-A1B2C",
      "status": "active",
      "expires_at": "2026-08-27T10:00:00.000000Z",
      "product": { "name": "OrdoB Estoque", "slug": "estoque" },
      "plan": { "name": "Starter" }
    }
  ]
}
```

---

### `GET /api/v1/licenses/{license}`

> 🔒 Autenticado

Detalhes de uma licença específica.

**Resposta 200:**
```json
{
  "license": { ... }
}
```

---

## Organizações

### `GET /api/v1/organizations`

> 🔒 Autenticado

Lista organizações do usuário.

**Resposta 200:**
```json
{
  "organizations": [
    {
      "id": 1,
      "uuid": "ORG-A1B2C3",
      "name": "Minha Empresa Ltda",
      "document": "12.345.678/0001-90",
      "licenses": [
        {
          "product": { "name": "OrdoB Estoque" }
        }
      ]
    }
  ]
}
```

---

### `POST /api/v1/organizations`

> 🔒 Autenticado

Cria uma nova organização.

**Body:**
```json
{
  "name": "Nova Empresa Ltda",
  "document": "98.765.432/0001-10"
}
```

**Resposta 201:**
```json
{
  "message": "Empresa criada com sucesso!",
  "organization": { ... }
}
```

---

### `GET /api/v1/organizations/{organization}`

> 🔒 Autenticado

Detalhes de uma organização.

**Resposta 200:**
```json
{
  "organization": {
    "id": 1,
    "uuid": "ORG-A1B2C3",
    "name": "Minha Empresa Ltda",
    "document": "12.345.678/0001-90",
    "licenses": [ ... ],
    "users": [
      { "id": 1, "name": "João Silva", "pivot": { "role": "owner" } }
    ]
  }
}
```

---

### `PUT /api/v1/organizations/{organization}`

> 🔒 Autenticado (apenas owner)

Atualiza dados da organização.

**Body:**
```json
{
  "name": "Nome Atualizado",
  "document": "11.111.111/0001-11"
}
```

---

### `DELETE /api/v1/organizations/{organization}`

> 🔒 Autenticado (apenas owner)

Exclui organização.

**Resposta 200:**
```json
{
  "message": "Empresa excluída com sucesso."
}
```

---

## Pagamentos

### `GET /api/v1/payments`

> 🔒 Autenticado

Lista pagamentos do usuário.

**Resposta 200:**
```json
{
  "payments": [
    {
      "id": 1,
      "uuid": "1",
      "amount": 29.90,
      "status": "received",
      "method": "Cartão de Crédito",
      "paid_at": "2026-07-27T10:00:00.000000Z",
      "created_at": "2026-07-27T10:00:00.000000Z",
      "description": "OrdoB Estoque — Starter",
      "subscription": {
        "id": 1,
        "status": "active",
        "next_billing": "2026-08-27T10:00:00.000000Z"
      }
    }
  ]
}
```

---

### `GET /api/v1/payments/{payment}`

> 🔒 Autenticado

Detalhes de um pagamento.

---

## Notificações

### `GET /api/v1/notifications`

> 🔒 Autenticado

Lista as últimas 20 notificações do usuário.

**Resposta 200:**
```json
{
  "notifications": [
    {
      "id": "abc123-def456",
      "type": "ticket_reply",
      "data": {
        "type": "ticket_reply",
        "ticket_id": 1,
        "ticket_subject": "Problema com licença",
        "message_id": 5,
        "message_preview": "Olá! Verificamos sua licença...",
        "from_support": true,
        "actor_name": "Suporte OrdoB",
        "has_attachments": false
      },
      "read_at": null,
      "created_at": "2026-07-27T10:00:00.000000Z",
      "is_read": false
    }
  ],
  "unread_count": 3
}
```

---

### `GET /api/v1/notifications/stream`

> 🔒 Autenticado (via token na query `?token=` para SSE)

**Server-Sent Events** — streaming de notificações em tempo real.

**Query params:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `token` | string | Token de acesso (necessário para SSE via EventSource) |

**Eventos:**
```
event: notification
data: { "id": "...", "type": "ticket_reply", "data": {...}, "read_at": null, ... }

event: unread_count
data: 3

: heartbeat
```

---

### `POST /api/v1/notifications/{id}/read`

> 🔒 Autenticado

Marca uma notificação como lida.

**Resposta 200:**
```json
{
  "message": "Notificação marcada como lida."
}
```

---

### `POST /api/v1/notifications/read-all`

> 🔒 Autenticado

Marca todas as notificações como lidas.

---

### `DELETE /api/v1/notifications/{id}`

> 🔒 Autenticado

Remove uma notificação.

---

## Tickets de Suporte

### `GET /api/v1/tickets`

> 🔒 Autenticado

Lista tickets do usuário logado.

**Resposta 200:**
```json
{
  "tickets": [
    {
      "id": 1,
      "uuid": "#A1B2C3",
      "subject": "Problema com renovação de licença",
      "status": "open",
      "priority": "media",
      "category": "suporte",
      "created_at": "2026-07-27T10:00:00.000000Z"
    }
  ]
}
```

---

### `POST /api/v1/tickets`

> 🔒 Autenticado

Abre um novo ticket de suporte.

**Body:**
```json
{
  "subject": "Problema com renovação de licença",
  "description": "Minha licença expirou mas o pagamento foi realizado.",
  "category": "suporte",
  "priority": "media"
}
```

| Campo | Obrigatório | Valores |
|-------|-------------|---------|
| `subject` | ✅ | string, max 255 |
| `description` | ✅ | string |
| `category` | ✅ | `suporte`, `faturamento`, `tecnico`, `outro` |
| `priority` | ✅ | `baixa`, `media`, `alta` |

**Resposta 201:**
```json
{
  "message": "Ticket criado com sucesso!",
  "ticket": {
    "id": 1,
    "uuid": "#A1B2C3",
    "subject": "Problema com renovação de licença",
    "status": "open",
    "priority": "media",
    "category": "suporte",
    "created_at": "2026-07-27T10:00:00.000000Z",
    "messages": [
      {
        "id": 1,
        "user_id": 1,
        "message": "Minha licença expirou mas o pagamento foi realizado.",
        "created_at": "2026-07-27T10:00:00.000000Z",
        "attachments": null
      }
    ]
  }
}
```

---

### `GET /api/v1/tickets/{ticket}`

> 🔒 Autenticado

Detalhes do ticket com todas as mensagens.

**Resposta 200:**
```json
{
  "ticket": {
    "id": 1,
    "uuid": "#A1B2C3",
    "subject": "Problema com renovação de licença",
    "status": "open",
    "priority": "media",
    "category": "suporte",
    "created_at": "2026-07-27T10:00:00.000000Z",
    "messages": [
      {
        "id": 1,
        "user_id": 1,
        "message": "Minha licença expirou mas o pagamento foi realizado.",
        "created_at": "2026-07-27T10:00:00.000000Z",
        "attachments": null
      },
      {
        "id": 2,
        "user_id": 2,
        "message": "Olá! Verificamos aqui e sua licença foi reativada.",
        "created_at": "2026-07-27T11:00:00.000000Z",
        "attachments": null
      }
    ]
  }
}
```

---

### `POST /api/v1/tickets/{ticket}/messages`

> 🔒 Autenticado

Adiciona mensagem ao ticket. Suporta upload de arquivos via `multipart/form-data`.

**Body (multipart/form-data):**
| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| `message` | string | ✅ |
| `attachments[]` | file[] | ❌ (max 5, até 10MB cada) |

**Tipos de arquivo aceitos:** `jpg`, `jpeg`, `png`, `gif`, `webp`, `pdf`, `doc`, `docx`, `xls`, `xlsx`, `txt`, `csv`

**Resposta 201:**
```json
{
  "message": "Mensagem adicionada!",
  "data": {
    "id": 3,
    "user_id": 1,
    "message": "Obrigado! Conseguir acessar novamente.",
    "created_at": "2026-07-27T12:00:00.000000Z",
    "attachments": [
      {
        "name": "comprovante.pdf",
        "path": "tickets/1/comprovante.pdf",
        "url": "https://api.ordob.com/storage/tickets/1/comprovante.pdf",
        "size": 102400,
        "type": "application/pdf"
      }
    ]
  }
}
```

---

### `GET /api/v1/tickets/{ticket}/messages/stream`

> 🔒 Autenticado (via query param `?token=` para SSE)

**Server-Sent Events** — streaming de novas mensagens em tempo real.

**Query params:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `last_id` | int | ID da última mensagem conhecida (para evitar duplicatas) |
| `token` | string | Token de acesso (necessário para SSE via EventSource) |

**Eventos:**
```
id: 3
event: ticket.message
data: {"id":3,"user_id":2,"message":"Olá! Sua licença foi reativada.","created_at":"...","attachments":null}

: heartbeat
```

---

### `GET /api/v1/tickets/{ticket}/messages/{messageId}/attachments/{attachmentIndex}`

> 🔒 Autenticado

Download de um anexo específico.

**Exemplo:** `GET /api/v1/tickets/1/messages/2/attachments/0`

**Resposta:** Stream do arquivo com headers `Content-Disposition: attachment`.

---

## Webhooks (Asaas)

### `POST /api/v1/webhooks/asaas`

> Público (endpoint para o Asaas)

Recebe eventos de pagamento do Asaas.

**Body (enviado pelo Asaas):**
```json
{
  "event": "PAYMENT_RECEIVED",
  "payment": {
    "id": "pay_123456",
    "value": 29.90,
    "subscription": "sub_789012"
  },
  "subscription": {
    "id": "sub_789012"
  }
}
```

**Eventos suportados:**
| Evento | Ação |
|--------|------|
| `PAYMENT_RECEIVED` | Ativa/renova licença, registra pagamento |
| `PAYMENT_OVERDUE` | Marca licença como `pending_payment` |
| `PAYMENT_REFUNDED` | Marca licença como `expired` |
| `SUBSCRIPTION_CANCELLED` | Marca licença como `expired` |

---

## Erros

### Estrutura padrão de erros

**Erro de validação (422):**
```json
{
  "errors": {
    "email": ["O campo email é obrigatório."],
    "password": ["A senha deve ter no mínimo 8 caracteres."]
  }
}
```

**Erro de autenticação (401):**
```json
{
  "message": "Email ou senha inválidos."
}
```

**Erro de permissão (403):**
```json
{
  "error": "Acesso negado."
}
```

**Não encontrado (404):**
```json
{
  "error": "Produto não encontrado."
}
```

---

## Modelos / Schemas

### User
```json
{
  "id": 1,
  "uuid": "USR-A1B2C3",
  "name": "João Silva",
  "email": "joao@exemplo.com",
  "phone": "(11) 99999-9999",
  "role": "user",
  "avatar": null,
  "current_organization_id": 1,
  "email_verified_at": null,
  "created_at": "2026-07-27T10:00:00.000000Z"
}
```

### Organization
```json
{
  "id": 1,
  "uuid": "ORG-A1B2C3",
  "name": "Minha Empresa Ltda",
  "document": "12.345.678/0001-90",
  "owner_id": 1,
  "created_at": "2026-07-27T10:00:00.000000Z"
}
```

### Product
```json
{
  "id": 1,
  "name": "OrdoB Estoque",
  "slug": "estoque",
  "description": "Sistema inteligente de controle de estoque com IA preditiva.",
  "tagline": "Controle de estoque com inteligência artificial",
  "icon": "package",
  "color": "#3B82F6",
  "is_active": true
}
```

### Plan
```json
{
  "id": 1,
  "name": "Starter",
  "price": 29.90,
  "description": "Para pequenos negócios",
  "features": ["Até 500 itens", "1 usuário", "Relatórios básicos"],
  "is_highlighted": false
}
```

### License
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "license_key": "ORDOB-EST-A1B2C",
  "status": "active",
  "expires_at": "2026-08-27T10:00:00.000000Z",
  "activated_at": "2026-07-27T10:00:00.000000Z"
}
```

### Ticket
```json
{
  "id": 1,
  "uuid": "#A1B2C3",
  "subject": "Problema com renovação",
  "status": "open",
  "priority": "media",
  "category": "suporte",
  "created_at": "2026-07-27T10:00:00.000000Z"
}
```

### TicketMessage
```json
{
  "id": 1,
  "user_id": 1,
  "message": "Descrição do problema...",
  "created_at": "2026-07-27T10:00:00.000000Z",
  "attachments": [
    {
      "name": "arquivo.pdf",
      "path": "tickets/1/arquivo.pdf",
      "url": "https://api.ordob.com/storage/tickets/1/arquivo.pdf",
      "size": 102400,
      "type": "application/pdf"
    }
  ]
}
```

### Notification
```json
{
  "id": "abc123-def456",
  "type": "ticket_reply",
  "data": {
    "type": "ticket_reply",
    "ticket_id": 1,
    "ticket_subject": "Problema com licença",
    "message_id": 5,
    "message_preview": "Olá! Verificamos sua licença...",
    "from_support": true,
    "actor_name": "Suporte OrdoB",
    "has_attachments": false
  },
  "read_at": null,
  "created_at": "2026-07-27T10:00:00.000000Z",
  "is_read": false
}
```

### Status de Licença / Ticket

| Status | Descrição |
|--------|-----------|
| `active` | Licença ativa |
| `expired` | Licença expirada |
| `blocked` | Licença bloqueada |
| `pending_payment` | Aguardando pagamento |
| `open` | Ticket aberto |
| `in_progress` | Ticket em andamento |
| `resolved` | Ticket resolvido |
| `closed` | Ticket fechado |

---

> **Última atualização:** 27 de Julho de 2026  
> **OrdoB Tecnologia** — [ordob.com](https://ordob.com)
