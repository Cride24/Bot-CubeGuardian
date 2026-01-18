# ⚙️ Configuration - Bot CubeGuardian

## 📋 **Vue d'ensemble**

Le bot utilise un système de configuration centralisé via des fichiers YAML/JSON pour gérer tous les paramètres.

---

## 📁 **Structure des fichiers de configuration**

```
config/
├── bot.yaml              # Configuration principale du bot
├── servers.yaml          # Informations des serveurs
├── discord.yaml          # Configuration Discord
├── messages.yaml         # Messages et phrases du bot
└── users.yaml            # Liste des utilisateurs autorisés
```

---

## 🔧 **Fichier principal : `bot.yaml`**

```yaml
# Configuration principale du bot CubeGuardian
# Versions vérifiées le 2025-01-16
bot:
  name: "CubeGuardian"
  version: "1.1.0"
  debug: false
  log_level: "INFO" # DEBUG, INFO, WARNING, ERROR

  # Versions des technologies (vérifiées avec sources officielles)
  technologies:
    python: "3.11+"
    discord_py: "2.6.3+"
    discord_api: "v10"
    powershell: "5.1+"
    docker: "20.10+"

# Timers et délais (en secondes)
timers:
  startup_timeout: 600 # 10 minutes pour le démarrage
  shutdown_delay: 600 # 10 minutes avant arrêt
  shutdown_confirm: 60 # 1 minute pour confirmer l'arrêt
  connectivity_check: 10 # 10 secondes entre vérifications
  reconnect_interval: 30 # 30 secondes entre tentatives

# Chemins des scripts (versions adaptées au bot)
scripts:
  # Scripts principaux
  wakeup_script: "./scripts/wakeup-pve-bot.ps1"
  shutdown_script: "./scripts/shutdown-pve-bot.ps1"

  # Scripts de vérification
  check_proxmox_script: "./scripts/check-proxmox-bot.ps1"
  check_minecraft_script: "./scripts/check-minecraft-bot.ps1"

  # Répertoire de travail
  working_directory: "./scripts"

  # Scripts de référence (originaux)
  reference_scripts:
    wakeup_original: "C:\\Users\\cedri\\Desktop\\Projet_Maison\\Serveur_local\\PVE\\scripts\\wakeup-pve.ps1"
    shutdown_original: "C:\\Users\\cedri\\Desktop\\Projet_Maison\\Serveur_local\\PVE\\scripts\\shutdown-pve.ps1"

# Logs
logging:
  file_enabled: true
  file_path: "./logs/cubeguardian.log"
  max_file_size: "10MB"
  backup_count: 5
  discord_logs: true

  # Rotation des logs par nombre de lignes
  max_lines: 200 # Limite de 200 lignes par fichier
  rotation_enabled: true # Rotation automatique activée
  keep_oldest: false # Supprimer les lignes les plus anciennes
```

---

## 🖥️ **Fichier serveurs : `servers.yaml`**

```yaml
# Configuration des serveurs
servers:
  proxmox:
    name: "LM150g6"
    ipv4: "192.168.1.245"
    mac_address: "00:23:7D:FD:C0:5C"
    ssh_user: "root"
    ssh_key_path: "C:\\Users\\cedri\\Desktop\\Projet_Maison\\Serveur_local\\ssh-keys\\pve\\pve-key"
    web_interface: "https://192.168.1.245:8006"

  minecraft:
    name: "Minecraft Server"
    ipv4: "192.168.1.245" # Même IP que Proxmox
    port: 25565
    timeout: 5 # Timeout pour test de connectivité
    startup_delay: 60 # Délai après démarrage Proxmox avant test Minecraft
```

---

## 💬 **Fichier Discord : `discord.yaml`**

```yaml
# Configuration Discord
discord:
  # Token du bot (à mettre dans .env pour la sécurité)
  token: "${DISCORD_BOT_TOKEN}"

  # Salons à surveiller
  channels:
    voice_channel: "L'écho-du-Cube"
    text_channel: "Salon-du-Cube"

  # Permissions requises
  intents:
    - "voice_states"
    - "members"
    - "guilds"
    - "messages"

  # Admin du bot
  admin:
    user_id: "123456789012345678" # ID Discord de l'admin
    dm_on_errors: true
    dm_on_startup: true
```

---

## 👥 **Fichier utilisateurs : `users.yaml`**

```yaml
# Utilisateurs autorisés
authorized_users:
  - user_id: "123456789012345678"
    username: "Admin"
    display_name: "Administrateur"
    permissions:
      - "start_server"
      - "stop_server"
      - "admin_commands"

  - user_id: "987654321098765432"
    username: "Player1"
    display_name: "Joueur 1"
    permissions:
      - "start_server"

  - user_id: "456789123456789123"
    username: "Player2"
    display_name: "Joueur 2"
    permissions:
      - "start_server"

# Groupes d'utilisateurs (optionnel)
groups:
  admins:
    - "123456789012345678"
  players:
    - "987654321098765432"
    - "456789123456789123"
```

---

## 🔧 **Scripts PowerShell adaptés au bot**

### **Structure des scripts**

```
Serveur_Docker/Bot-CubeGuardian/
├── scripts/
│   ├── wakeup-pve-bot.ps1      # Wake-on-LAN pour le bot
│   ├── shutdown-pve-bot.ps1    # Arrêt serveur pour le bot
│   ├── check-proxmox-bot.ps1   # Vérification connectivité Proxmox
│   └── check-minecraft-bot.ps1 # Vérification serveur Minecraft
```

### **Caractéristiques des scripts bot**

#### **1. Mode silencieux**

- Pas de messages utilisateur
- Pas de confirmations interactives
- Logs structurés uniquement

#### **2. Retour JSON standardisé**

```json
{
  "success": true,
  "message": "Opération réussie",
  "timestamp": "2025-01-16 14:30:00",
  "details": {
    "target": "192.168.1.245",
    "operation": "wake_on_lan"
  }
}
```

#### **3. Codes de retour standardisés**

- `0` : Succès
- `1` : Erreur de paramètres
- `2` : Erreur réseau
- `3` : Erreur de connectivité
- `4` : Timeout
- `5` : Erreur de permissions

### **Configuration des scripts**

```yaml
# Paramètres des scripts
script_parameters:
  wakeup:
    mac_address: "00:23:7D:FD:C0:5C"
    target_host: "192.168.1.245"
    timeout: 30
    quiet_mode: true

  shutdown:
    target_host: "192.168.1.245"
    ssh_user: "root"
    ssh_key_path: "./keys/proxmox_key"
    timeout: 30
    quiet_mode: true

  check_proxmox:
    target_host: "192.168.1.245"
    timeout: 10
    quiet_mode: true

  check_minecraft:
    target_host: "192.168.1.245"
    port: 25565
    timeout: 5
    quiet_mode: true
```

---

## 💬 **Fichier messages : `messages.yaml`**

```yaml
# Messages et phrases du bot
messages:
  # Messages de démarrage
  startup:
    request: "🟡 Démarrage du serveur demandé par {user}"
    in_progress: "🟡 Démarrage en cours... Veuillez patienter"
    success: "🟢 Serveur opérationnel ! Minecraft disponible sur {server_ip}:{port}"
    failed: "❌ Échec du démarrage du serveur après {timeout} minutes"
    timeout: "⏰ Serveur non disponible après {timeout} minutes"

  # Messages de logs
  logs:
    startup_initiated: "Démarrage initié par {user}"
    server_available: "Serveur disponible après {time} minutes"
    startup_failed: "Échec du démarrage du serveur après {time} minutes"
    proxmox_connectivity_failed: "Échec de la connectivité Proxmox"
    minecraft_connectivity_failed: "Échec de la connectivité Minecraft"
    proxmox_shutdown: "Arrêt de Proxmox"
    shutdown_scheduled: "Arrêt programmé dans {time} minutes"
    shutdown_cancelled: "Arrêt annulé. Utilisateur autorisé détecté. {user}"
    shutdown_in_progress: "Arrêt du serveur en cours..."
    server_shutdown: "Serveur arrêté à {time}"
    server_not_shutdown: "Serveur non arrêté à {time}"

  # Messages d'arrêt
  shutdown:
    initiated: "⏰ Aucun utilisateur autorisé détecté. Arrêt dans {delay} minutes..."
    cancelled: "✅ Arrêt annulé. Utilisateur autorisé détecté. Bienvenu {user}"
    in_progress: "🔴 Arrêt du serveur en cours..."
    confirmed: "⚫ Serveur arrêté avec succès"
    failed: "❌ Échec de l'arrêt du serveur"

  # Messages d'erreur
  errors:
    connectivity: "🔌 Problème de connectivité détecté"
    script_error: "⚠️ Erreur lors de l'exécution du script {script}"
    permission_denied: "🚫 Permission refusée pour {user}"
    server_unreachable: "🌐 Serveur {server} inaccessible"

  # Messages d'information
  info:
    bot_started: "🤖 CubeGuardian démarré et en surveillance"
    user_joined: "👋 {user} a rejoint le salon vocal"
    user_left: "👋 {user} a quitté le salon vocal"
    monitoring_active: "👁️ Surveillance active du salon {channel}"

  # Messages d'alerte admin
  admin_alerts:
    startup_failed: "🚨 ALERTE ADMIN : Échec du démarrage du serveur"
    shutdown_failed: "🚨 ALERTE ADMIN : Échec de l'arrêt du serveur"
    connectivity_lost: "🚨 ALERTE ADMIN : Perte de connectivité"
    script_error: "🚨 ALERTE ADMIN : Erreur script {script} - {error}"
    bot_crashed: "🚨 ALERTE ADMIN : Le bot a planté - {error}"
```

---

## 🔐 **Fichier d'environnement : `.env`**

```bash
# Variables d'environnement sensibles
DISCORD_BOT_TOKEN=ton_token_discord_ici
DISCORD_GUILD_ID=id_de_ton_serveur_discord
DISCORD_ADMIN_ID=id_discord_de_l_admin

# Configuration optionnelle
BOT_DEBUG=false
LOG_LEVEL=INFO
```

---

## 📊 **Fichier de configuration avancée : `advanced.yaml`**

```yaml
# Configuration avancée (optionnelle)
advanced:
  # Gestion des erreurs
  error_handling:
    max_retries: 3
    retry_delay: 5
    fallback_mode: true

  # Performance
  performance:
    max_concurrent_operations: 2
    operation_timeout: 30
    memory_limit: "512MB"

  # Sécurité
  security:
    rate_limiting: true
    max_requests_per_minute: 60
    blacklist_enabled: false

  # Monitoring
  monitoring:
    health_check_interval: 60
    metrics_enabled: true
    alert_thresholds:
      cpu_usage: 80
      memory_usage: 85
      disk_usage: 90
```

---

## 🔄 **Validation de la configuration**

### **Script de validation : `validate_config.py`**

```python
import yaml
import os
from pathlib import Path

def validate_config():
    """Valide tous les fichiers de configuration"""
    config_files = [
        "bot.yaml",
        "servers.yaml",
        "discord.yaml",
        "messages.yaml",
        "users.yaml"
    ]

    for config_file in config_files:
        if not os.path.exists(config_file):
            print(f"❌ Fichier manquant : {config_file}")
            return False

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print(f"✅ {config_file} : Configuration valide")
        except yaml.YAMLError as e:
            print(f"❌ {config_file} : Erreur YAML - {e}")
            return False

    return True

if __name__ == "__main__":
    validate_config()
```

---

## 📝 **Exemple de configuration complète**

### **Structure de dossiers recommandée :**

```
Bot-CubeGuardian/
├── config/
│   ├── bot.yaml
│   ├── servers.yaml
│   ├── discord.yaml
│   ├── messages.yaml
│   ├── users.yaml
│   └── advanced.yaml
├── scripts/
│   ├── wakeup-pve.ps1
│   └── shutdown-pve.ps1
├── logs/
├── .env
└── bot.py
```

---

## 🛠️ **Outils de configuration**

### **Générateur de configuration : `generate_config.py`**

```python
def generate_default_config():
    """Génère une configuration par défaut"""
    # Code pour créer les fichiers de config par défaut
    pass

def update_config(key, value):
    """Met à jour une valeur de configuration"""
    # Code pour modifier la configuration
    pass
```

---

## 📋 **Checklist de configuration**

- [ ] Token Discord configuré dans `.env`
- [ ] IDs des salons Discord corrects
- [ ] Liste des utilisateurs autorisés complète
- [ ] Chemins des scripts PowerShell valides
- [ ] Adresses IP et MAC du serveur Proxmox
- [ ] Port Minecraft configuré
- [ ] Messages personnalisés définis
- [ ] Permissions Discord accordées
- [ ] Configuration validée avec `validate_config.py`

---

**Dernière mise à jour :** 2025-01-16  
**Version :** 1.0.0
