# 🤖 Bot Discord CubeGuardian

## 📋 **Vue d'ensemble**

Bot Discord automatisé pour la surveillance et la gestion du serveur Proxmox/Minecraft basée sur l'activité vocale Discord.

## 🎯 **Objectifs**

- ✅ Automatisation du démarrage/arrêt du serveur Proxmox
- ✅ Surveillance des salons vocaux Discord
- ✅ Gestion des utilisateurs autorisés
- ✅ Notifications en temps réel
- ✅ Réduction de la consommation électrique

## 🏗️ **Architecture**

```
Bot-CubeGuardian/
├── config/                 # Fichiers de configuration
│   ├── bot.yaml           # Configuration principale
│   ├── servers.yaml       # Configuration des serveurs
│   ├── discord.yaml       # Configuration Discord
│   ├── messages.yaml      # Messages du bot
│   └── users.yaml         # Utilisateurs autorisés
├── src/                   # Code source Python
│   ├── bot.py            # Bot principal
│   ├── server_manager.py # Gestion des serveurs (interface)
│   ├── server_manager/   # Modules Python natifs
│   │   ├── wake_on_lan.py        # Wake-on-LAN natif
│   │   ├── ssh_manager.py        # Gestion SSH natif
│   │   ├── connectivity_checker.py # Tests de connectivité
│   │   ├── minecraft_checker.py  # Vérification Minecraft
│   │   └── server_manager.py     # Module principal unifié
│   ├── voice_monitor.py  # Surveillance vocale
│   ├── user_manager.py   # Gestion des utilisateurs
│   ├── message_manager.py # Gestion des messages
│   ├── config_manager.py # Gestion de la configuration
│   └── log_manager.py    # Gestion des logs
├── logs/                  # Fichiers de logs
├── keys/                  # Clés SSH
├── tests/                 # Tests unitaires
├── docker/               # Configuration Docker
├── requirements.txt      # Dépendances Python
├── .env.template        # Template variables d'environnement
└── README.md            # Ce fichier
```

## 🚀 **Installation**

### **Prérequis**

- Python 3.11+
- Token Discord Bot
- Accès SSH au serveur Proxmox
- Clé SSH pour Proxmox

### **Configuration**

1. Copier `.env.template` vers `.env` et configurer les variables
2. Configurer les fichiers YAML dans `config/`
3. Installer les dépendances : `pip install -r requirements.txt`
4. Lancer le bot : `python src/bot.py`

## 🔧 **Technologies**

- **Python 3.11+** : Langage principal
- **discord.py 2.6.3+** : API Discord
- **wakeonlan 3.0+** : Wake-on-LAN natif Python
- **paramiko 3.4+** : Client SSH natif Python
- **YAML** : Configuration
- **Docker** : Containerisation

## 📊 **Fonctionnalités**

### **Surveillance vocale**

- Détection des connexions/déconnexions
- Vérification des utilisateurs autorisés
- Gestion des timers d'arrêt

### **Gestion du serveur**

- Wake-on-LAN du serveur Proxmox
- Surveillance de la disponibilité Minecraft
- Arrêt propre du serveur

### **Notifications**

- Messages dans le salon textuel
- Messages privés à l'admin
- Logs détaillés

## 🔒 **Sécurité**

- Token Discord sécurisé
- Permissions minimales
- Validation des entrées
- Rate limiting Discord
- Logs sécurisés

## 📚 **Documentation**

Voir le dossier `Cahier-des-charges/` pour la documentation complète.

## 🐳 **Déploiement Docker**

```bash
# Construction de l'image
docker build -t cubeguardian .

# Lancement avec Docker Compose
docker-compose up -d
```

## 🧪 **Tests**

```bash
# Tests unitaires
python -m pytest tests/

# Tests d'intégration
python -m pytest tests/integration/
```

## 📈 **Monitoring**

- Health checks automatiques
- Métriques de performance
- Alertes admin
- Logs avec rotation

---

**Version :** 1.1.0  
**Dernière mise à jour :** 2025-01-16  
**Statut :** En développement
