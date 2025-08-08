# Odoo MCP Server

Un serveur MCP (Model Context Protocol) pour l'intégration avec Odoo, déployable sur Render.

## Fonctionnalités

- **Connexion sécurisée** à Odoo via XML-RPC
- **Opérations CRUD** complètes (Create, Read, Update, Delete)
- **Recherche avancée** avec domaines et filtres
- **Gestion des modèles** et inspection des champs
- **Appels de méthodes** personnalisées
- **Déploiement facile** sur Render

## Outils disponibles

### `odoo_connect`
Établit une connexion à une instance Odoo.
```json
{
  "url": "https://your-odoo.com",
  "database": "your_db",
  "username": "admin",
  "password": "password"
}
```

### `odoo_search`
Recherche des enregistrements dans un modèle Odoo.
```json
{
  "model": "res.partner",
  "domain": [["is_company", "=", true]],
  "fields": ["name", "email"],
  "limit": 50
}
```

### `odoo_create`
Crée un nouvel enregistrement.
```json
{
  "model": "res.partner",
  "values": {
    "name": "Nouvelle Entreprise",
    "email": "contact@entreprise.com",
    "is_company": true
  }
}
```

### `odoo_write`
Met à jour des enregistrements existants.
```json
{
  "model": "res.partner",
  "ids": [1, 2, 3],
  "values": {"phone": "+33123456789"}
}
```

### `odoo_unlink`
Supprime des enregistrements.
```json
{
  "model": "res.partner",
  "ids": [1, 2, 3]
}
```

### `odoo_call`
Appelle une méthode personnalisée sur un modèle.
```json
{
  "model": "sale.order",
  "method": "action_confirm",
  "args": [],
  "kwargs": {}
}
```

### `odoo_get_models`
Liste les modèles disponibles.
```json
{
  "filter": "sale"
}
```

### `odoo_get_fields`
Obtient les informations des champs d'un modèle.
```json
{
  "model": "res.partner"
}
```

### `odoo_count`
Compte les enregistrements correspondant à un domaine.
```json
{
  "model": "res.partner",
  "domain": [["is_company", "=", true]]
}
```

## Installation locale

1. Clonez le repository
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement :
```bash
cp .env.example .env
# Éditez .env avec vos paramètres Odoo
```

4. Lancez le serveur :
```bash
python -m odoo_mcp_server
```

## Déploiement sur Render

### Option 1: Déploiement Docker (Recommandé)

1. Connectez votre repository à Render
2. Choisissez "Web Service" 
3. Sélectionnez "Docker" comme environnement
4. Configurez les variables d'environnement :
   - `ODOO_URL` : https://your-odoo-instance.com
   - `ODOO_DATABASE` : your_database_name
   - `ODOO_USERNAME` : your_username
   - `ODOO_PASSWORD` : your_password

5. Render utilisera automatiquement le `Dockerfile` inclus

### Option 2: Déploiement Python

1. Connectez votre repository à Render
2. Choisissez "Web Service" avec Python
3. Configurez les mêmes variables d'environnement
4. Render détectera automatiquement :
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m odoo_mcp_server`

### Configuration automatique

Utilisez le fichier `render.yaml` inclus pour une configuration automatique.

## Configuration

### Variables d'environnement

- `ODOO_URL` : URL de votre instance Odoo
- `ODOO_DATABASE` : Nom de la base de données
- `ODOO_USERNAME` : Nom d'utilisateur Odoo
- `ODOO_PASSWORD` : Mot de passe
- `ODOO_SSL_VERIFY` : Vérification SSL (true/false)
- `ODOO_TIMEOUT` : Timeout de connexion en secondes
- `ODOO_DEFAULT_LIMIT` : Limite par défaut pour les recherches

## Utilisation avec MCP

Ajoutez ce serveur à votre configuration MCP :

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["-m", "odoo_mcp_server"],
      "env": {
        "ODOO_URL": "https://your-odoo.com",
        "ODOO_DATABASE": "your_db",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "password"
      }
    }
  }
}
```

## Sécurité

- Utilisez HTTPS pour les connexions Odoo
- Stockez les mots de passe dans des variables d'environnement
- Limitez les permissions utilisateur dans Odoo
- Activez la vérification SSL en production

## Développement

Structure du projet :
```
odoo_mcp_server/
├── __init__.py
├── __main__.py        # Lance l'API HTTP (FastAPI)
├── main.py            # Serveur MCP (stdio)
└── odoo_client.py     # Client Odoo XML-RPC
```

## Outils supplémentaires

### `odoo_update_lead_contact`
Met à jour un lead CRM (`crm.lead`).
```json
{
  "lead_id": 42,
  "values": {
    "contact_name": "Jean Dupont",
    "email_from": "jean.dupont@example.com",
    "phone": "+33123456789"
  }
}
```

### `odoo_update_contact`
Met à jour un contact (`res.partner`).
```json
{
  "partner_id": 10,
  "values": {
    "name": "Entreprise ABC",
    "email": "contact@abc.com",
    "phone": "+33111222333"
  }
}
```

### `odoo_read_group`
Reporting par agrégation.
```json
{
  "model": "crm.lead",
  "domain": [["type", "=", "opportunity"]],
  "fields": ["expected_revenue:sum"],
  "groupby": ["stage_id"],
  "limit": 50
}
```

### `web_search`
Recherche web via Tavily (nécessite `TAVILY_API_KEY`).
```json
{
  "query": "Odoo CRM best practices",
  "max_results": 5,
  "search_depth": "basic"
}
```

## Licence

MIT License