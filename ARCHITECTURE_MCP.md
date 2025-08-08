### Odoo MCP Server — Architecture et Guide

Ce document décrit l’architecture du serveur MCP pour Odoo, son mode d’exécution (stdio MCP et API HTTP), et propose des pistes d’amélioration conformes à la spécification Model Context Protocol (MCP).

### Objectifs

- Exposer des outils MCP pour manipuler Odoo (connexion, CRUD, appels de méthodes, introspection).
- Proposer une API HTTP simple pour intégrations externes (FastAPI).
- Déploiement facile via Docker/Docker Compose/Render.

### Arborescence pertinente

```
MPC_server_Odoo/
├─ odoo_mcp_server/
│  ├─ __main__.py         # Point d’entrée: lance le serveur HTTP
│  ├─ main.py             # Serveur MCP en stdio (outils MCP)
│  ├─ http_server.py      # API HTTP (FastAPI + Pydantic)
│  └─ odoo_client.py      # Client XML-RPC Odoo (async via executors)
├─ Dockerfile             # Image Python 3.11-slim, exécute `python -m odoo_mcp_server`
├─ docker-compose.yml     # Service exposé sur le port 8000
├─ README.md              # Présentation des outils (à aligner avec le code actuel)
├─ HTTP_API_README.md     # Détail des endpoints HTTP
├─ DOCKER.md              # Guide Docker/Render
└─ requirements.txt       # Dépendances (FastAPI, Uvicorn, MCP, dotenv...)
```

### Composants

- Outils MCP (stdio) — `odoo_mcp_server/main.py`
  - Déclare les outils `odoo_connect`, `odoo_search`, `odoo_create`, `odoo_write`, `odoo_unlink`, `odoo_call`, `odoo_get_models`, `odoo_get_fields`, `odoo_count`.
  - Transport stdio via `mcp.server.stdio`.

```1:22:/Users/lucasbometon/Documents/code/gradio/MCP_Odoo/MPC_server_Odoo/odoo_mcp_server/main.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
# ...
class OdooMCPServer:
    def __init__(self):
        self.server = Server("odoo-mcp-server")
        # ...
```

- API HTTP (FastAPI) — `odoo_mcp_server/http_server.py`
  - Endpoints: `/` et `/health`, `POST /connect`, `/search`, `/create`, `/write`, `/unlink`, `/call`, `/models`, `/fields`, `/count`.
  - Démarrage via `__main__`.

```77:97:/Users/lucasbometon/Documents/code/gradio/MCP_Odoo/MPC_server_Odoo/odoo_mcp_server/http_server.py
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Odoo MCP HTTP API Server",
        "version": "0.2.0",
        "connected": odoo_client is not None,
        "endpoints": ["/connect","/search","/create","/write","/unlink","/call","/models","/fields","/count"]
    }
```

- Point d’entrée — `odoo_mcp_server/__main__.py`
  - Lance systématiquement l’API HTTP.

```5:9:/Users/lucasbometon/Documents/code/gradio/MCP_Odoo/MPC_server_Odoo/odoo_mcp_server/__main__.py
from .http_server import run_http_server
if __name__ == "__main__":
    run_http_server()
```

- Client Odoo XML‑RPC — `odoo_mcp_server/odoo_client.py`
  - Auth, `search_read`, `create`, `write`, `unlink`, `fields_get`, `search_count`, `call_method`.

### Flux d’exécution

- Mode MCP (stdio) pour intégration avec un hôte MCP (IDE/LLM) via JSON‑RPC sur stdin/stdout.
- Mode HTTP pour intégrations applicatives classiques via REST.

### Lancement

- Local (HTTP par défaut)
  - Variables: `ODOO_URL`, `ODOO_DATABASE`, `ODOO_USERNAME`, `ODOO_PASSWORD`, `PORT` (8000 par défaut)
  - Commande: `python -m odoo_mcp_server`

- Docker
  - Build: `docker build -t odoo-mcp-server .`
  - Run: `docker run -p 8000:8000 -e ODOO_URL=... -e ODOO_DATABASE=... -e ODOO_USERNAME=... -e ODOO_PASSWORD=... odoo-mcp-server`

- Docker Compose
  - `docker-compose up -d`

### API HTTP (résumé)

- `GET /`, `GET /health`
- `POST /connect` → établit la session Odoo
- `POST /search` | `/create` | `/write` | `/unlink`
- `POST /call` (méthodes personnalisées), `/models`, `/fields`, `/count`

Voir `HTTP_API_README.md` pour les schémas détaillés.

### Paramétrage MCP (stdio)

Dans un host MCP, configurer la commande stdio (ex.: `python -m odoo_mcp_server` pour HTTP, ou utiliser le serveur stdio depuis `main.py` si intégré):

```169:184:/Users/lucasbometon/Documents/code/gradio/MCP_Odoo/MPC_server_Odoo/README.md
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["-m", "odoo_mcp_server"]
    }
  }
}
```

### Avis et cohérence actuelle

- Le code exécute l’API HTTP par défaut (via `__main__`). La doc `README.md` mentionne encore `server.py` et une commande `python -m odoo_mcp_server.server` qui n’existe plus. À aligner.
- `pyproject.toml` déclare un script `odoo-mcp-server = "odoo_mcp_server.server:main"` et dépendance `xmlrpc-client` (inutile, `xmlrpc.client` est dans la stdlib). À corriger/simplifier si usage packaging.
- `Dockerfile` copie `.env.example` qui n’est pas présent → build cassant potentiel. À retirer ou ajouter le fichier.
- `http_server.py` maintient un `odoo_client` global → limites en concurrence/multi-sessions.
- `odoo_client.py` crée un contexte SSL mais ne l’emploie pas dans `ServerProxy` (transport personnalisé requis si besoin de context SSL avancé).
- Le dépôt contient `venv/` commité → à exclure du VCS.

### Conformité à la spéc MCP (Context7)

- Transports MCP officiels: stdio et HTTP « Streamable » (POST + SSE). Réf: `Model Context Protocol – Transports` (Context7 `/modelcontextprotocol/specification`).
- Le mode stdio dans `main.py` est conforme MCP.
- L’API HTTP actuelle est une façade REST (non MCP-HTTP). Si l’objectif est un serveur MCP distant, viser le transport HTTP « Streamable » (POST + SSE, en-têtes `MCP-Protocol-Version`, gestion de session `Mcp-Session-Id`, validation d’Origin). Sinon conserver REST comme interface end-user et stdio pour MCP.

### Améliorations prioritaires (simples et utiles)

1) Documentation & packaging
- Aligner `README.md` avec l’exécution réelle: `python -m odoo_mcp_server` (HTTP), et préciser comment lancer le mode stdio MCP (`main.py`).
- Corriger `pyproject.toml`: supprimer `xmlrpc-client`, synchroniser versions avec `requirements.txt`, mettre un entrypoint valide ou retirer les scripts si non utilisés.

2) Docker
- Supprimer `COPY .env.example .env` ou ajouter le fichier; éviter d’échouer au build.
- Option: multi-stage build et `--user` déjà OK.

3) Sécurité HTTP
- Ajouter authentification simple (ex. Bearer token en variable d’env) sur tous les endpoints mutateurs.
- Restreindre CORS et valider `Origin` si exposition publique.
- En local, lier sur `127.0.0.1` par défaut; n’exposer `0.0.0.0` qu’en container.

4) Robustesse Odoo
- Implémenter timeouts et retries exponentiels sur les appels XML‑RPC.
- Gérer pagination côté `/search` si `limit` grand et exposer `offset`.
- Exploiter réellement un transport SSL custom si nécessaire (validation stricte, option de désactivation en DEV via env `ODOO_SSL_VERIFY=false`).

5) Concurrence & sessions
- Éviter l’état global FastAPI: stocker une session identifiée (token) renvoyée par `/connect` et utilisée dans les appels suivants, ou ré-instancier le client par requête à partir des en-têtes/vars.

6) Observabilité
- Ajouter `logging` structuré (niveau, corrélation requêtes), métriques (Prometheus) et `/metrics` optionnel.

7) Conformité MCP HTTP (optionnel)
- Si besoin d’un serveur MCP sur HTTP: implémenter l’endpoint unique MCP (POST/GET SSE), en-têtes `MCP-Protocol-Version`, `Mcp-Session-Id`, et les règles de résumabilité SSE.

8) Qualité
- Passer les tests en `pytest` + CI (GitHub Actions), tests unitaires pour `odoo_client.py` (mocks XML‑RPC) et tests d’intégration HTTP.
- Ajouter une `LICENSE` et retirer `venv/` du dépôt.

### Roadmap courte (proposée)

- Semaine 1: Alignement docs/entrypoints, sécurité HTTP basique (token), suppression état global.
- Semaine 2: Timeouts/retries/pagination, tests Pytest + CI, nettoyage packaging.
- Semaine 3: Option MCP HTTP streamable (POST+SSE) si nécessaire.

### Références (Context7)

- Spécification des transports MCP (stdio, HTTP Streamable), gestion de sessions et en-têtes version: `Context7` → `/modelcontextprotocol/specification` (sections Transports, Session Management, Protocol Version Header).

---

Ce serveur est fonctionnel et bien structuré pour un usage Docker/Render. Les ajustements ci‑dessus améliorent la cohérence, la sécurité et la conformité MCP tout en restant simples à mettre en œuvre.


