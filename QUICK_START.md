# 🚀 Guide de Démarrage Rapide - Bot CubeGuardian

## 📋 **Vue d'ensemble**

Ce guide vous permet de démarrer rapidement le Bot CubeGuardian en quelques étapes simples.

## ⚡ **Démarrage Express (5 minutes)**

### **1. Prérequis**

- ✅ Python 3.11+ installé
- ✅ Token Discord Bot créé
- ✅ Serveur Discord configuré
- ✅ Clé SSH pour Proxmox

### **2. Configuration rapide**

```bash
# 1. Cloner/copier le projet
cd Serveur_Docker/Bot-CubeGuardian

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
copy .env.template .env
# Éditer .env avec vos valeurs

# 4. Configurer les fichiers YAML
# Éditer config/discord.yaml avec vos IDs Discord
# Éditer config/users.yaml avec vos utilisateurs autorisés
```

### **3. Test rapide**

```bash
# Tester la configuration
python test_bot.py

# Si tout est OK, lancer le bot
python src/bot.py
```

## 🔧 **Configuration détaillée**

### **Variables d'environnement (.env)**

```env
# OBLIGATOIRE
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_discord_guild_id_here
DISCORD_ADMIN_ID=123456789012345678

# SERVEURS
PROXMOX_HOST=192.168.1.245
PROXMOX_MAC=00:23:7D:FD:C0:5C
MINECRAFT_HOST=192.168.1.245
MINECRAFT_PORT=25565
```

### **Configuration Discord (config/discord.yaml)**

```yaml
discord:
  token: "${DISCORD_BOT_TOKEN}"
  channels:
    voice_channel: "L'écho-du-Cube" # Nom de votre salon vocal
    text_channel: "Salon-du-Cube" # Nom de votre salon textuel
  admin:
    user_id: "123456789012345678" # Votre ID Discord
```

### **Utilisateurs autorisés (config/users.yaml)**

```yaml
authorized_users:
  - user_id: "123456789012345678"
    username: "Admin"
    display_name: "Administrateur"
    permissions:
      - "start_server"
      - "stop_server"
      - "admin_commands"
```

## 🐳 **Démarrage avec Docker**

### **1. Construction de l'image**

```bash
# Construire l'image Docker
docker build -t cubeguardian .

# Ou avec Docker Compose
docker-compose build
```

### **2. Configuration des secrets**

```bash
# Créer le dossier secrets
mkdir secrets

# Créer les fichiers de secrets
echo "your_discord_bot_token" > secrets/discord_token.txt
echo "123456789012345678" > secrets/admin_user_id.txt
# Copier votre clé SSH vers secrets/proxmox_ssh_key
```

### **3. Lancement**

```bash
# Avec Docker Compose
docker-compose up -d

# Vérifier les logs
docker-compose logs -f cubeguardian
```

## 🧪 **Tests et validation**

### **Test de configuration**

```bash
# Test complet des modules
python test_bot.py

# Test des modules Python natifs
python -m pytest tests/test_server_manager_native.py -v
```

### **Test de connectivité**

```bash
# Test des modules natifs
python -c "
import asyncio
from src.server_manager.connectivity_checker import ConnectivityChecker
from src.server_manager.minecraft_checker import MinecraftChecker

async def test():
    checker = ConnectivityChecker(None)
    result = await checker.check_proxmox_connectivity('192.168.1.245')
    print('Proxmox:', result['success'])

    minecraft = MinecraftChecker(None)
    result = await minecraft.check_minecraft_connectivity('192.168.1.245', 25565)
    print('Minecraft:', result['success'])

asyncio.run(test())
"
```

## 🔍 **Dépannage rapide**

### **Problèmes courants**

| Problème                 | Solution                                                   |
| ------------------------ | ---------------------------------------------------------- |
| Token Discord invalide   | Vérifier le token dans .env                                |
| Salon vocal non trouvé   | Vérifier le nom dans discord.yaml                          |
| Utilisateur non autorisé | Ajouter l'ID dans users.yaml                               |
| Module Python échoue     | Vérifier les dépendances (pip install -r requirements.txt) |
| Bot ne se connecte pas   | Vérifier les intents Discord                               |
| Erreur SSH               | Vérifier la clé SSH et les permissions                     |

### **Logs et debugging**

```bash
# Activer le mode debug
# Dans .env: BOT_DEBUG=true, LOG_LEVEL=DEBUG

# Consulter les logs
tail -f logs/cubeguardian.log

# Logs Docker
docker-compose logs -f cubeguardian
```

## 📊 **Vérification du fonctionnement**

### **1. Bot connecté**

- ✅ Bot en ligne sur Discord
- ✅ Message "🤖 CubeGuardian démarré et en surveillance"
- ✅ Surveillance active du salon vocal

### **2. Test de démarrage**

- ✅ Rejoindre le salon vocal "L'écho-du-Cube"
- ✅ Message "🟡 Démarrage du serveur demandé par [utilisateur]"
- ✅ Wake-on-LAN envoyé
- ✅ Message "🟢 Serveur opérationnel !"

### **3. Test d'arrêt**

- ✅ Quitter le salon vocal
- ✅ Message "⏰ Aucun utilisateur autorisé détecté. Arrêt dans 10 minutes..."
- ✅ Attendre 10 minutes
- ✅ Message "🔴 Arrêt du serveur en cours..."

## 🚨 **Sécurité**

### **Checklist sécurité**

- [ ] Token Discord dans .env (jamais en dur)
- [ ] Clés SSH protégées
- [ ] Permissions minimales du bot
- [ ] Utilisateurs autorisés limités
- [ ] Logs sans données sensibles

### **Permissions Discord minimales**

- ✅ Envoyer des messages
- ✅ Voir les salons
- ✅ Se connecter aux salons vocaux
- ❌ Administrateur (DANGEREUX)

## 📚 **Ressources**

- 📖 [Documentation complète](README.md)
- 📋 [Cahier des charges](Cahier-des-charges/)
- 🔧 [Configuration avancée](config/)
- 🐳 [Déploiement Docker](docker-compose.yml)

## 🆘 **Support**

En cas de problème :

1. Vérifier les logs : `logs/cubeguardian.log`
2. Tester la configuration : `python test_bot.py`
3. Vérifier les permissions Discord
4. Consulter la documentation complète

---

**🎉 Félicitations ! Votre Bot CubeGuardian est prêt à fonctionner !**
