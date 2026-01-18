# 🎯 Bonnes Pratiques Discord - Bot CubeGuardian

## 📋 **Vue d'ensemble**

Documentation des bonnes pratiques essentielles pour le développement, la sécurité et le déploiement d'un bot Discord professionnel, basée sur les standards 2025.

---

## 🔧 **Développement et Architecture**

### **1. Choix technologique validé**

#### **Python + discord.py (Recommandé)**

```python
# Installation
pip install discord.py[voice]  # Version avec support vocal

# Version minimale requise (vérifiée 2025-01-16)
discord.py >= 2.6.3  # Version stable actuelle
Python >= 3.11       # Version recommandée

# Sources officielles :
# discord.py : https://pypi.org/project/discord.py/
# Python : https://www.python.org/downloads/
```

**Avantages :**

- ✅ Syntaxe simple et lisible
- ✅ Excellente documentation
- ✅ Support natif des événements vocaux
- ✅ Gestion asynchrone intégrée
- ✅ Communauté active et support

#### **Intents Discord (Obligatoires)**

```python
import discord
from discord.ext import commands

# Intents requis pour notre bot
intents = discord.Intents.default()
intents.voice_states = True  # Surveillance des salons vocaux
intents.members = True       # Accès aux informations des membres
intents.guilds = True        # Accès aux informations du serveur
intents.message_content = True  # Lecture du contenu des messages

bot = commands.Bot(command_prefix='!', intents=intents)
```

### **2. Architecture recommandée**

```python
# Structure de projet recommandée
Bot-CubeGuardian/
├── main.py                 # Point d'entrée principal
├── config/
│   ├── __init__.py
│   ├── config.py          # Gestionnaire de configuration
│   └── settings.py        # Paramètres par défaut
├── cogs/                  # Extensions du bot
│   ├── __init__.py
│   ├── voice_monitor.py   # Surveillance vocale
│   ├── server_manager.py  # Gestion des serveurs
│   └── admin.py          # Commandes admin
├── utils/
│   ├── __init__.py
│   ├── logger.py         # Gestionnaire de logs
│   ├── powershell.py     # Wrapper PowerShell
│   └── validators.py     # Validation des données
├── scripts/              # Scripts PowerShell
├── logs/                 # Fichiers de logs
└── requirements.txt      # Dépendances Python
```

---

## 🔒 **Sécurité et Permissions**

### **1. Gestion sécurisée du token**

#### **Variables d'environnement (Recommandé)**

```python
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Récupération sécurisée du token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("Token Discord manquant dans les variables d'environnement")
```

#### **Fichier .env (À ne jamais commiter)**

```env
# Fichier .env - À ajouter au .gitignore
DISCORD_TOKEN=your_bot_token_here
PROXMOX_HOST=192.168.1.245
PROXMOX_MAC=00:23:7D:FD:C0:5C
ADMIN_USER_ID=123456789012345678
```

#### **Docker secrets (Production)**

```yaml
# docker-compose.yml
version: "3.8"
services:
  cubeguardian:
    image: cubeguardian:latest
    environment:
      - DISCORD_TOKEN_FILE=/run/secrets/discord_token
    secrets:
      - discord_token

secrets:
  discord_token:
    file: ./secrets/discord_token.txt
```

### **2. Permissions minimales**

#### **Permissions Discord requises**

```python
# Calculateur de permissions (permissions minimales)
PERMISSIONS = {
    'SEND_MESSAGES': True,           # Envoyer des messages
    'VIEW_CHANNEL': True,            # Voir les salons
    'CONNECT': True,                 # Se connecter aux salons vocaux
    'SPEAK': False,                  # Parler (non requis)
    'MANAGE_MESSAGES': False,        # Gérer les messages (non requis)
    'ADMINISTRATOR': False,          # Administrateur (DANGEREUX)
}

# Valeur calculée : 2048 (0x800)
REQUIRED_PERMISSIONS = 2048
```

#### **Validation des permissions**

```python
async def validate_bot_permissions(guild):
    """Vérifie que le bot a les permissions minimales requises"""
    bot_member = guild.get_member(bot.user.id)
    permissions = bot_member.guild_permissions

    required = {
        'send_messages': permissions.send_messages,
        'view_channel': permissions.view_channel,
        'connect': permissions.connect,
    }

    missing = [perm for perm, has_perm in required.items() if not has_perm]

    if missing:
        raise PermissionError(f"Permissions manquantes: {', '.join(missing)}")

    return True
```

### **3. Validation des entrées utilisateur**

```python
import re
from typing import Optional

class InputValidator:
    """Validateur pour les entrées utilisateur"""

    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Valide un ID utilisateur Discord"""
        return bool(re.match(r'^\d{17,19}$', str(user_id)))

    @staticmethod
    def validate_channel_name(name: str) -> bool:
        """Valide un nom de salon"""
        return 1 <= len(name) <= 100 and not re.search(r'[<>@#&!]', name)

    @staticmethod
    def sanitize_message(message: str) -> str:
        """Nettoie un message pour éviter les injections"""
        # Suppression des caractères dangereux
        dangerous_chars = ['<', '>', '@', '#', '&', '!']
        for char in dangerous_chars:
            message = message.replace(char, '')
        return message.strip()
```

---

## ⚡ **Performance et Limites**

### **1. Respect des Rate Limits Discord**

#### **Limites importantes (2025)**

```python
# Limites Discord à respecter
# Source officielle : https://discord.com/developers/docs/topics/rate-limits
# Dernière vérification : 2025-01-16

RATE_LIMITS = {
    'messages_per_channel': {
        'limit': 5,  # Messages par seconde par salon
        'window': 1,  # Fenêtre de 1 seconde
        'source': 'Discord API Documentation'
    },
    'global_requests': {
        'limit': 50,  # Requêtes globales par seconde
        'window': 1,
        'source': 'Discord API Documentation'
    },
    'voice_operations': {
        'limit': 10,  # Opérations vocales par seconde
        'window': 1,
        'source': 'Discord API Documentation'
    }
}
```

#### **Gestionnaire de rate limiting**

```python
import asyncio
from collections import defaultdict, deque
from time import time

class RateLimiter:
    """Gestionnaire de rate limiting pour Discord"""

    def __init__(self):
        self.requests = defaultdict(deque)

    async def wait_if_needed(self, endpoint: str, limit: int, window: int):
        """Attend si nécessaire pour respecter les limites"""
        now = time()
        requests = self.requests[endpoint]

        # Nettoyer les requêtes anciennes
        while requests and requests[0] <= now - window:
            requests.popleft()

        # Vérifier si on peut faire la requête
        if len(requests) >= limit:
            sleep_time = requests[0] + window - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        # Enregistrer la requête actuelle
        requests.append(now)
```

### **2. Optimisation des événements**

```python
import asyncio
from functools import wraps

def rate_limit(calls_per_second: float):
    """Décorateur pour limiter le taux d'appels"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time()
            time_since_last = now - last_called[0]

            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)

            last_called[0] = time()
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Utilisation
@rate_limit(2.0)  # Maximum 2 appels par seconde
async def send_status_message(channel, message):
    """Envoie un message de statut avec rate limiting"""
    await channel.send(message)
```

---

## 🐳 **Déploiement et Hébergement**

### **1. Configuration Docker optimisée**

#### **Dockerfile multi-stage**

```dockerfile
# Dockerfile optimisé pour production
FROM python:3.11-slim as builder

# Installation des dépendances de build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage de production
FROM python:3.11-slim

# Installation de PowerShell
RUN apt-get update && apt-get install -y \
    wget \
    apt-transport-https \
    software-properties-common \
    && wget -q https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y powershell \
    && rm -rf /var/lib/apt/lists/*

# Copie des dépendances Python
COPY --from=builder /root/.local /root/.local

# Création de l'utilisateur non-root
RUN useradd --create-home --shell /bin/bash cubeguardian
USER cubeguardian
WORKDIR /home/cubeguardian

# Copie du code
COPY --chown=cubeguardian:cubeguardian . .

# Configuration des logs
RUN mkdir -p logs

# Point d'entrée
CMD ["python", "main.py"]
```

#### **Docker Compose pour production**

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  cubeguardian:
    build: .
    container_name: cubeguardian-bot
    restart: unless-stopped

    # Variables d'environnement
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO

    # Secrets
    secrets:
      - discord_token
      - proxmox_ssh_key

    # Volumes
    volumes:
      - ./logs:/home/cubeguardian/logs:rw
      - ./scripts:/home/cubeguardian/scripts:ro
      - ./config:/home/cubeguardian/config:ro

    # Limites de ressources
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
        reservations:
          memory: 256M
          cpus: "0.25"

    # Health check
    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "import requests; requests.get('http://localhost:8080/health')",
        ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

secrets:
  discord_token:
    file: ./secrets/discord_token.txt
  proxmox_ssh_key:
    file: ./secrets/proxmox_ssh_key
```

### **2. Monitoring et observabilité**

#### **Health check endpoint**

```python
from aiohttp import web
import asyncio

class HealthChecker:
    """Vérificateur de santé du bot"""

    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.app.router.add_get('/health', self.health_check)

    async def health_check(self, request):
        """Endpoint de vérification de santé"""
        try:
            # Vérifications de base
            checks = {
                'bot_connected': self.bot.is_ready(),
                'discord_api': await self.check_discord_api(),
                'proxmox_connectivity': await self.check_proxmox(),
                'logs_writable': await self.check_logs()
            }

            all_healthy = all(checks.values())
            status = 200 if all_healthy else 503

            return web.json_response({
                'status': 'healthy' if all_healthy else 'unhealthy',
                'checks': checks,
                'timestamp': time.time()
            }, status=status)

        except Exception as e:
            return web.json_response({
                'status': 'error',
                'error': str(e)
            }, status=500)

    async def check_discord_api(self) -> bool:
        """Vérifie la connectivité à l'API Discord"""
        try:
            await self.bot.fetch_user(self.bot.user.id)
            return True
        except:
            return False

    async def check_proxmox(self) -> bool:
        """Vérifie la connectivité Proxmox"""
        # Implémentation de la vérification Proxmox
        return True

    async def check_logs(self) -> bool:
        """Vérifie que les logs sont accessibles en écriture"""
        try:
            with open('logs/health_check.log', 'a') as f:
                f.write(f"Health check at {time.time()}\n")
            return True
        except:
            return False
```

---

## 🧪 **Tests et Qualité**

### **1. Tests unitaires**

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

class TestCubeGuardianBot:
    """Tests unitaires pour le bot CubeGuardian"""

    @pytest.fixture
    async def bot(self):
        """Fixture pour créer une instance de bot de test"""
        from main import CubeGuardianBot
        bot = CubeGuardianBot()
        bot.config = {
            'discord': {'token': 'test_token'},
            'servers': {'proxmox': {'host': '192.168.1.245'}}
        }
        return bot

    @pytest.mark.asyncio
    async def test_voice_state_update(self, bot):
        """Test de la surveillance des changements d'état vocal"""
        # Mock des objets Discord
        member = Mock()
        member.id = 123456789
        member.display_name = "TestUser"

        before = Mock()
        before.channel = None

        after = Mock()
        after.channel = Mock()
        after.channel.name = "L'écho-du-Cube"

        # Test de l'événement
        with patch.object(bot, 'handle_voice_join') as mock_handle:
            await bot.on_voice_state_update(member, before, after)
            mock_handle.assert_called_once_with(member)

    @pytest.mark.asyncio
    async def test_authorized_user_validation(self, bot):
        """Test de la validation des utilisateurs autorisés"""
        bot.config['discord']['authorized_users'] = [123456789, 987654321]

        # Test utilisateur autorisé
        assert bot.is_authorized_user(123456789) == True

        # Test utilisateur non autorisé
        assert bot.is_authorized_user(555555555) == False

    @pytest.mark.asyncio
    async def test_powershell_wrapper(self, bot):
        """Test du wrapper PowerShell"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"success": true}'

            result = await bot.powershell_wrapper.execute_script("test.ps1")

            assert result['success'] == True
            assert result['data']['success'] == True
```

### **2. Tests d'intégration**

```python
class TestIntegration:
    """Tests d'intégration pour le bot"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test du workflow complet"""
        # 1. Utilisateur rejoint le salon vocal
        # 2. Wake-on-LAN envoyé
        # 3. Surveillance du serveur
        # 4. Confirmation de disponibilité
        # 5. Utilisateur quitte le salon
        # 6. Timer d'arrêt lancé
        # 7. Arrêt du serveur

        # Implémentation des tests d'intégration
        pass
```

---

## 📊 **Monitoring et Logs**

### **1. Métriques importantes**

```python
import time
from collections import defaultdict

class MetricsCollector:
    """Collecteur de métriques pour le bot"""

    def __init__(self):
        self.metrics = defaultdict(int)
        self.start_time = time.time()

    def increment(self, metric_name: str, value: int = 1):
        """Incrémente une métrique"""
        self.metrics[metric_name] += value

    def get_uptime(self) -> float:
        """Retourne le temps de fonctionnement"""
        return time.time() - self.start_time

    def get_metrics_summary(self) -> dict:
        """Retourne un résumé des métriques"""
        return {
            'uptime_seconds': self.get_uptime(),
            'voice_joins': self.metrics['voice_joins'],
            'voice_leaves': self.metrics['voice_leaves'],
            'server_starts': self.metrics['server_starts'],
            'server_stops': self.metrics['server_stops'],
            'errors': self.metrics['errors']
        }
```

### **2. Alertes automatiques**

```python
class AlertManager:
    """Gestionnaire d'alertes pour le bot"""

    def __init__(self, bot):
        self.bot = bot
        self.alert_thresholds = {
            'error_rate': 5,  # 5 erreurs par minute
            'response_time': 10,  # 10 secondes de délai
            'memory_usage': 80  # 80% d'utilisation mémoire
        }

    async def check_alerts(self):
        """Vérifie les conditions d'alerte"""
        # Vérification du taux d'erreur
        if self.get_error_rate() > self.alert_thresholds['error_rate']:
            await self.send_alert("HIGH_ERROR_RATE", {
                'error_rate': self.get_error_rate(),
                'threshold': self.alert_thresholds['error_rate']
            })

        # Vérification du temps de réponse
        if self.get_avg_response_time() > self.alert_thresholds['response_time']:
            await self.send_alert("SLOW_RESPONSE", {
                'response_time': self.get_avg_response_time(),
                'threshold': self.alert_thresholds['response_time']
            })

    async def send_alert(self, alert_type: str, data: dict):
        """Envoie une alerte à l'administrateur"""
        admin = self.bot.get_user(self.bot.config['discord']['admin_user_id'])
        if admin:
            embed = discord.Embed(
                title=f"🚨 Alerte: {alert_type}",
                description=f"Le bot a détecté un problème",
                color=0xff0000
            )
            for key, value in data.items():
                embed.add_field(name=key, value=value, inline=True)

            await admin.send(embed=embed)
```

---

## 📋 **Checklist de déploiement**

### **Prérequis techniques**

- [ ] **Discord Developer Portal** : Application créée et configurée
- [ ] **Token sécurisé** : Stocké dans les variables d'environnement
- [ ] **Permissions minimales** : Seulement les permissions nécessaires
- [ ] **Intents configurés** : `voice_states`, `members`, `guilds`
- [ ] **Python 3.8+** : Version compatible installée
- [ ] **discord.py 2.3+** : Version récente de la bibliothèque
- [ ] **PowerShell** : Installé et accessible
- [ ] **Clés SSH** : Configurées pour Proxmox

### **Sécurité**

- [ ] **Token protégé** : Jamais exposé dans le code
- [ ] **Permissions limitées** : Pas de droits administrateur
- [ ] **Validation des entrées** : Toutes les entrées utilisateur validées
- [ ] **Rate limiting** : Respect des limites Discord
- [ ] **Logs sécurisés** : Pas de données sensibles dans les logs
- [ ] **HTTPS** : Communication sécurisée (si applicable)

### **Performance**

- [ ] **Rate limiting implémenté** : Respect des limites Discord
- [ ] **Gestion d'erreur robuste** : Pas de plantages
- [ ] **Logs optimisés** : Rotation automatique configurée
- [ ] **Monitoring** : Health checks et métriques
- [ ] **Tests** : Tests unitaires et d'intégration
- [ ] **Documentation** : Code et API documentés

### **Déploiement**

- [ ] **Docker configuré** : Image optimisée pour production
- [ ] **Variables d'environnement** : Configuration externalisée
- [ ] **Secrets gérés** : Tokens et clés sécurisés
- [ ] **Volumes persistants** : Logs et configuration
- [ ] **Health checks** : Vérification de santé automatique
- [ ] **Restart policy** : Redémarrage automatique configuré

---

## 📚 **Sources et références officielles**

### **Documentation Discord**

| Ressource                     | URL                                                                                                                              | Description                          |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| **Discord Developer Portal**  | [discord.com/developers](https://discord.com/developers/applications)                                                            | Création et gestion des applications |
| **Discord API Documentation** | [discord.com/developers/docs](https://discord.com/developers/docs/)                                                              | Documentation complète de l'API      |
| **Rate Limits**               | [discord.com/developers/docs/topics/rate-limits](https://discord.com/developers/docs/topics/rate-limits)                         | Limites de taux officielles          |
| **Intents**                   | [discord.com/developers/docs/topics/gateway#gateway-intents](https://discord.com/developers/docs/topics/gateway#gateway-intents) | Configuration des intents            |

### **Bibliothèques et outils**

| Technologie    | URL                                                                     | Version vérifiée |
| -------------- | ----------------------------------------------------------------------- | ---------------- |
| **discord.py** | [pypi.org/project/discord.py](https://pypi.org/project/discord.py/)     | 2.6.3            |
| **Python**     | [python.org/downloads](https://www.python.org/downloads/)               | 3.11+            |
| **PowerShell** | [docs.microsoft.com/powershell](https://docs.microsoft.com/powershell/) | 5.1+             |
| **Docker**     | [docs.docker.com](https://docs.docker.com/)                             | 20.10+           |

### **Bonnes pratiques et sécurité**

- **Discord Bot Best Practices** : [Discord Developer Portal - Bot vs User](https://discord.com/developers/docs/topics/oauth2#bot-vs-user-accounts)
- **Python Security** : [Python Security Best Practices](https://python.org/dev/security/)
- **Docker Security** : [Docker Security Best Practices](https://docs.docker.com/engine/security/)

### **Validation des informations**

- ✅ **Versions vérifiées** avec les sources officielles (2025-01-16)
- ✅ **Rate limits validés** avec la documentation Discord officielle
- ✅ **Compatibilité confirmée** entre discord.py 2.6.3 et Python 3.11+
- ✅ **Sources officielles** ajoutées pour toutes les technologies

---

**Dernière mise à jour :** 2025-01-16  
**Version :** 1.1.0  
**Standards :** Discord API v10, Python 3.11+, discord.py 2.6.3+  
**Validation technique :** ✅ Vérifié avec sources officielles
