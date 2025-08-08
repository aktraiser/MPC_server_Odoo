# 🐳 Docker Deployment Guide

Ce guide explique comment déployer le serveur MCP Odoo avec Docker sur Render.

## 📋 Prérequis

- Docker installé localement (pour les tests)
- Compte GitHub
- Compte Render
- Instance Odoo accessible

## 🏗️ Architecture Docker

```
Dockerfile
├── Base: Python 3.11-slim
├── Dependencies: MCP, requests, python-dotenv
├── Security: Non-root user
├── Health check: Import test
└── Port: 8000
```

## 🚀 Déploiement Local (Test)

### 1. Build de l'image
```bash
docker build -t odoo-mcp-server .
```

### 2. Run du container
```bash
docker run -d \
  --name odoo-mcp-server \
  -p 8000:8000 \
  -e ODOO_URL=https://your-odoo.com \
  -e ODOO_DATABASE=your_db \
  -e ODOO_USERNAME=admin \
  -e ODOO_PASSWORD=password \
  odoo-mcp-server
```

### 3. Avec Docker Compose
```bash
# Créer un fichier .env avec vos variables
cp .env.example .env

# Lancer avec docker-compose
docker-compose up -d
```

## 🌐 Déploiement sur Render

### 1. Configuration automatique
Render détecte automatiquement le `Dockerfile` et utilise la configuration dans `render.yaml`.

### 2. Variables d'environnement requises
```
ODOO_URL=https://your-odoo-instance.com
ODOO_DATABASE=your_database_name
ODOO_USERNAME=your_username
ODOO_PASSWORD=your_password
PORT=8000
```

### 3. Étapes de déploiement
1. **Push vers GitHub**
   ```bash
   git add .
   git commit -m "Add Docker configuration"
   git push origin main
   ```

2. **Créer un Web Service sur Render**
   - Connecter le repository GitHub
   - Render détecte automatiquement Docker
   - Configurer les variables d'environnement

3. **Déployer**
   - Render build automatiquement l'image
   - Deploy et expose sur HTTPS

## 🧪 Tests Docker

### Test automatique
```bash
python test_docker.py
```

### Test manuel
```bash
# Build
docker build -t odoo-mcp-test .

# Run
docker run --rm -p 8001:8000 \
  -e ODOO_URL=https://demo.odoo.com \
  -e ODOO_DATABASE=demo \
  -e ODOO_USERNAME=admin \
  -e ODOO_PASSWORD=admin \
  odoo-mcp-test

# Test health
docker exec odoo-mcp-test python -c "import odoo_mcp_server; print('OK')"
```

## 📊 Monitoring

### Health Check
Le container inclut un health check qui vérifie :
- Import du module principal
- Disponibilité des dépendances

### Logs
```bash
# Logs du container
docker logs odoo-mcp-server

# Logs en temps réel
docker logs -f odoo-mcp-server
```

## 🔧 Optimisations

### Image Size
- Base image: `python:3.11-slim` (~45MB)
- Dependencies optimisées
- Multi-stage build possible pour réduire davantage

### Security
- Non-root user (`appuser`)
- Minimal system dependencies
- No cache pip install

### Performance
- Python bytecode compilation disabled
- Unbuffered output
- Health check optimisé

## 🐛 Troubleshooting

### Container ne démarre pas
```bash
# Vérifier les logs
docker logs container_name

# Vérifier la configuration
docker inspect container_name
```

### Problèmes de connexion Odoo
```bash
# Test de connectivité
docker exec container_name ping your-odoo-domain.com

# Test des variables d'environnement
docker exec container_name env | grep ODOO
```

### Problèmes de port
```bash
# Vérifier les ports exposés
docker port container_name

# Tester la connectivité
curl http://localhost:8000/health
```

## 📈 Scaling sur Render

Render permet de :
- Auto-scaling basé sur la charge
- Multiple instances
- Load balancing automatique
- SSL/TLS automatique

## 🔐 Sécurité

### Variables d'environnement
- Jamais dans le code source
- Utiliser Render Environment Variables
- Rotation régulière des mots de passe

### Network
- HTTPS uniquement sur Render
- Connexions Odoo sécurisées (SSL)
- Firewall Render intégré

## 📚 Ressources

- [Render Docker Guide](https://render.com/docs/docker)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [MCP Documentation](https://modelcontextprotocol.io/)

---

✅ **Le serveur MCP Odoo est maintenant prêt pour un déploiement Docker sur Render !**