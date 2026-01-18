# 💬 Messages et Notifications - Bot CubeGuardian

## 📋 **Vue d'ensemble**

Définition complète des messages, notifications et phrases utilisés par le bot dans toutes les situations.

---

## 🎯 **Types de messages**

### **1. Messages d'information** ℹ️

- Statut du bot
- Actions en cours
- Confirmations d'opérations

### **2. Messages d'alerte** ⚠️

- Problèmes détectés
- Erreurs non critiques
- Avertissements

### **3. Messages d'erreur** ❌

- Échecs d'opérations
- Problèmes de connectivité
- Erreurs critiques

### **4. Messages d'admin** 🚨

- Alertes critiques
- Notifications privées
- Rapports d'erreur

### **5. Messages de commandes** 🎮

- Demandes de confirmation
- Feedback utilisateur
- Messages de cooldown
- Validation des permissions

---

## 📝 **Messages par catégorie**

### **🎮 COMMANDES INTERACTIVES (Nouveau)**

#### **Détection de commande**

```
🤖 **Commande détectée : Redémarrage Minecraft**
⚠️ Cette action va redémarrer le serveur Minecraft et déconnecter tous les joueurs connectés.
**Êtes-vous sûr(e) de vouloir continuer ?**

Répondez par **oui** ou **non** dans les 60 secondes.
```

#### **Permission refusée**

```
🚫 **Permission refusée**
Seuls les joueurs autorisés peuvent exécuter cette commande.
```

#### **Cooldown actif**

```
⏳ **Cooldown actif**
Vous devez attendre encore **{minutes} minutes** avant de pouvoir exécuter cette commande.
```

#### **Confirmation reçue**

```
✅ **Confirmation reçue**
🔄 Redémarrage du serveur Minecraft en cours...
```

#### **Annulation**

```
❌ **Redémarrage annulé**
Aucune action n'a été effectuée.
```

#### **Timeout confirmation**

```
⏰ **Délai d'attente dépassé**
Redémarrage annulé par manque de confirmation.
```

#### **Redémarrage en cours**

```
🔄 **Redémarrage en cours...**
⏱️ Surveillance du processus - Maximum 5 minutes
📊 Statut : En cours de redémarrage...
```

#### **Redémarrage réussi**

```
✅ **Serveur Minecraft redémarré avec succès !**
⏱️ Temps de redémarrage : **{time} secondes**
🎮 Le serveur est maintenant disponible pour les connexions.
```

#### **Redémarrage échoué**

```
❌ **Échec du redémarrage du serveur Minecraft**
🔧 Le serveur n'a pas pu être redémarré dans les délais impartis.
📞 Un administrateur a été notifié automatiquement.
```

#### **Aide commandes**

```
🆘 **Aide - Commandes disponibles**
🎮 **Redémarrer Minecraft :** "@CubeGuardian redémarrer le serveur minecraft"
📝 **Variantes acceptées :** restart, reboot, relancer
⚠️ **Restrictions :** Seuls les joueurs autorisés - Cooldown 10 minutes
```

---

## 📝 **Messages par catégorie**

### **🟢 DÉMARRAGE DU SERVEUR**

#### **Demande de démarrage**

```
🟡 **Démarrage du serveur demandé par {user}**
⏰ Veuillez patienter pendant l'initialisation...
```

#### **Démarrage en cours**

```
🟡 **Démarrage en cours...**
📡 Magic Packet envoyé au serveur Proxmox
⏱️ Temps estimé : 2-3 minutes
```

#### **Surveillance du démarrage**

```
👁️ **Surveillance du démarrage active**
🔄 Vérification de la disponibilité...
⏰ Délai maximum : 10 minutes
```

#### **Serveur opérationnel**

```
🟢 **Serveur opérationnel !**
🎮 Minecraft disponible sur {server_ip}:{port}
✅ Prêt à jouer !
```

#### **Échec du démarrage**

```
❌ **Échec du démarrage du serveur**
⏰ Serveur non disponible après 10 minutes
🔧 Vérifiez la configuration ou contactez l'admin
```

---

### **🔴 ARRÊT DU SERVEUR**

#### **Démarrage du timer d'arrêt**

```
⏰ **Aucun utilisateur autorisé détecté**
🕐 Arrêt du serveur dans {delay} minutes...
👥 Rejoignez le salon vocal pour annuler
```

#### **Timer d'arrêt actif**

```
⏱️ **Timer d'arrêt actif**
🕐 Temps restant : {remaining_time} minutes
👥 {authorized_users} utilisateur(s) autorisé(s) requis pour annuler
```

#### **Annulation de l'arrêt**

```
✅ **Arrêt annulé !**
👋 {user} a rejoint le salon vocal
🟢 Serveur maintenu en fonctionnement
```

#### **Arrêt en cours**

```
🔴 **Arrêt du serveur en cours...**
📡 Commande d'arrêt envoyée au serveur Proxmox
⏱️ Temps estimé : 1 minute
```

#### **Arrêt confirmé**

```
⚫ **Serveur arrêté avec succès**
💤 Serveur Proxmox éteint
🔋 Économie d'énergie activée
```

#### **Échec de l'arrêt**

```
❌ **Échec de l'arrêt du serveur**
⚠️ Le serveur n'a pas répondu à la commande d'arrêt après 1 minute
🔧 Intervention manuelle requise
```

---

### **👥 ACTIVITÉ DES UTILISATEURS**

#### **Utilisateur rejoint**

```
👋 **{user} a rejoint le salon vocal**
🎮 {user} est maintenant dans "L'écho-du-Cube"
👥 {total_users} utilisateur(s) autorisé(s) présent(s)
```

#### **Utilisateur quitte**

```
👋 **{user} a quitté le salon vocal**
👥 {remaining_users} utilisateur(s) autorisé(s) restant(s)
```

#### **Utilisateur non autorisé**

```
🚫 **Accès refusé**
❌ {user} n'est pas autorisé à utiliser ce bot
📋 Contactez l'admin pour obtenir l'accès
```

---

### **🤖 STATUT DU BOT**

#### **Bot démarré**

```
🤖 **CubeGuardian démarré et en surveillance**
👁️ Surveillance active du salon "L'écho-du-Cube"
📊 Statut : {bot_state}
🕐 Démarré le {startup_time}
```

#### **Bot en maintenance**

```
🔧 **Mode maintenance activé**
⏸️ Surveillance temporairement suspendue
📋 {maintenance_reason}
```

#### **Bot redémarré**

```
🔄 **CubeGuardian redémarré**
✅ Reconnexion réussie
👁️ Surveillance reprise
```

---

### **🔌 CONNECTIVITÉ ET RÉSEAU**

#### **Problème de connectivité**

```
🔌 **Problème de connectivité détecté**
⚠️ Impossible de contacter le serveur Proxmox
🔄 Tentative de reconnexion en cours...
```

#### **Connectivité rétablie**

```
✅ **Connectivité rétablie**
🌐 Connexion au serveur Proxmox restaurée
🟢 Surveillance normale reprise
```

#### **Serveur inaccessible**

```
🌐 **Serveur inaccessible**
❌ Le serveur {server_name} ne répond pas
🔧 Vérifiez l'état du serveur
```

---

### **⚠️ ERREURS ET PROBLÈMES**

#### **Erreur de script**

```
⚠️ **Erreur lors de l'exécution du script**
📄 Script : {script_name}
❌ Erreur : {error_message}
🔧 Vérifiez la configuration
```

#### **Erreur de permission**

```
🚫 **Erreur de permission**
❌ Impossible d'exécuter : {operation}
🔑 Vérifiez les permissions du bot
```

#### **Erreur de configuration**

```
⚙️ **Erreur de configuration**
❌ Paramètre manquant : {parameter}
📋 Vérifiez le fichier de configuration
```

---

## 🚨 **Messages d'alerte admin (privés)**

### **Échec critique du démarrage**

```
🚨 **ALERTE ADMIN - Échec du démarrage**

❌ Le serveur n'a pas pu démarrer après 10 minutes
📊 Détails :
   • Utilisateur : {user}
   • Heure : {timestamp}
   • Erreur : {error_details}

🔧 Actions recommandées :
   • Vérifier l'état du serveur Proxmox
   • Contrôler la configuration Wake-on-LAN
   • Vérifier les logs système
```

### **Échec critique de l'arrêt**

```
🚨 **ALERTE ADMIN - Échec de l'arrêt**

❌ Le serveur n'a pas répondu à la commande d'arrêt
📊 Détails :
   • Heure de la demande : {timestamp}
   • Délai d'attente : 1 minute
   • Erreur : {error_details}

🔧 Actions recommandées :
   • Arrêt manuel du serveur
   • Vérifier la connectivité SSH
   • Contrôler les logs système
```

### **Perte de connectivité**

```
🚨 **ALERTE ADMIN - Perte de connectivité**

🔌 Le bot ne peut plus communiquer avec le serveur
📊 Détails :
   • Serveur : {server_name}
   • IP : {server_ip}
   • Dernière connexion : {last_connection}
   • Tentatives : {retry_count}/3

🔧 Actions recommandées :
   • Vérifier l'état du réseau
   • Contrôler l'état du serveur
   • Redémarrer le bot si nécessaire
```

### **Erreur critique du bot**

```
🚨 **ALERTE ADMIN - Erreur critique du bot**

💥 Le bot a rencontré une erreur critique
📊 Détails :
   • Erreur : {error_type}
   • Contexte : {error_context}
   • Heure : {timestamp}
   • État : {bot_state}

🔧 Actions recommandées :
   • Redémarrer le bot
   • Vérifier les logs
   • Contacter le développeur si persistant
```

### **Bot planté**

```
🚨 **ALERTE ADMIN - Le bot a planté**

💥 CubeGuardian s'est arrêté de manière inattendue
📊 Détails :
   • Heure du crash : {crash_time}
   • Dernière action : {last_action}
   • Erreur : {crash_error}

🔧 Actions recommandées :
  • Redémarrer le bot immédiatement
  • Vérifier les logs de crash
  • Analyser la cause du problème
```

#### **Alerte échec redémarrage (Nouveau)**

```
🚨 **ALERTE - Échec redémarrage Minecraft**

**Utilisateur :** {user_name} ({user_id})
**Commande :** Redémarrage conteneur LXC 105
**Horodatage :** {timestamp}
**Durée :** Timeout après 5 minutes

**Détails techniques :**
- API Proxmox : {api_status}
- Conteneur LXC : {container_status}
- Port Minecraft : {minecraft_port_status}

**Action recommandée :** Vérifier manuellement le conteneur LXC 105
```

#### **Alerte spam commandes (Nouveau)**

```
🚨 **ALERTE - Détection spam commandes**

**Utilisateur :** {user_name} ({user_id})
**Tentatives :** {attempt_count} en {duration} minutes
**Dernière tentative :** {last_attempt}

**Actions automatiques :**
- Cooldown forcé : {forced_cooldown} minutes
- Logs détaillés activés

**Action recommandée :** Surveiller l'activité de cet utilisateur
```

---

## 📊 **Messages de statistiques**

### **Rapport quotidien**

```
📊 **Rapport quotidien - {date}**

🟢 Démarrages réussis : {successful_startups}
❌ Démarrages échoués : {failed_startups}
🔴 Arrêts réussis : {successful_shutdowns}
⚠️ Arrêts échoués : {failed_shutdowns}
👥 Utilisateurs actifs : {active_users}
⏱️ Temps de fonctionnement : {uptime}

💡 Statistiques :
   • Taux de réussite : {success_rate}%
   • Temps moyen de démarrage : {avg_startup_time}
   • Économie d'énergie : {energy_saved} heures
```

### **Rapport hebdomadaire**

```
📈 **Rapport hebdomadaire - Semaine {week}**

📊 Activité de la semaine :
   • Démarrages : {weekly_startups}
   • Arrêts : {weekly_shutdowns}
   • Utilisateurs uniques : {unique_users}
   • Heures de fonctionnement : {total_hours}

🎯 Performance :
   • Disponibilité : {availability}%
   • Temps de réponse moyen : {avg_response_time}
   • Erreurs : {error_count}

💡 Recommandations :
   {recommendations}
```

---

## 🎨 **Formatage et emojis**

### **Emojis utilisés**

| Catégorie        | Emoji | Usage                     |
| ---------------- | ----- | ------------------------- |
| **Succès**       | 🟢 ✅ | Opérations réussies       |
| **En cours**     | 🟡 ⏰ | Actions en cours          |
| **Erreur**       | ❌ ⚠️ | Erreurs et problèmes      |
| **Arrêt**        | 🔴 ⚫ | Arrêts et fermetures      |
| **Utilisateurs** | 👥 👋 | Activité des utilisateurs |
| **Serveur**      | 🖥️ 🎮 | Serveurs et services      |
| **Réseau**       | 🌐 🔌 | Connectivité              |
| **Bot**          | 🤖 🔧 | État du bot               |
| **Admin**        | 🚨    | Alertes critiques         |

### **Formatage des messages**

```python
# Template de message
MESSAGE_TEMPLATE = """
{emoji} **{title}**

{content}

{footer}
"""

# Exemple d'utilisation
def format_message(emoji: str, title: str, content: str, footer: str = ""):
    return MESSAGE_TEMPLATE.format(
        emoji=emoji,
        title=title,
        content=content,
        footer=footer
    )
```

---

## 🔄 **Variables dynamiques**

### **Variables disponibles**

| Variable             | Description                     | Exemple               |
| -------------------- | ------------------------------- | --------------------- |
| `{user}`             | Nom d'utilisateur Discord       | "Player1"             |
| `{user_id}`          | ID Discord de l'utilisateur     | "123456789"           |
| `{server_ip}`        | IP du serveur Minecraft         | "192.168.1.245"       |
| `{port}`             | Port du serveur Minecraft       | "25565"               |
| `{delay}`            | Délai en minutes                | "10"                  |
| `{remaining_time}`   | Temps restant                   | "7"                   |
| `{total_users}`      | Nombre total d'utilisateurs     | "3"                   |
| `{authorized_users}` | Utilisateurs autorisés présents | "2"                   |
| `{timestamp}`        | Horodatage                      | "2025-01-16 14:30:00" |
| `{bot_state}`        | État actuel du bot              | "SURVEILLANCE"        |
| `{error_details}`    | Détails de l'erreur             | "Connection timeout"  |

### **Fonction de remplacement**

```python
def replace_variables(message: str, variables: dict) -> str:
    """Remplace les variables dans un message"""
    for key, value in variables.items():
        message = message.replace(f"{{{key}}}", str(value))
    return message

# Exemple d'utilisation
variables = {
    "user": "Player1",
    "server_ip": "192.168.1.245",
    "port": "25565"
}

message = "🎮 {user} peut maintenant jouer sur {server_ip}:{port}"
formatted_message = replace_variables(message, variables)
# Résultat : "🎮 Player1 peut maintenant jouer sur 192.168.1.245:25565"
```

---

## 📋 **Configuration des messages**

### **Fichier messages.yaml (extrait)**

```yaml
messages:
  startup:
    request: "🟡 **Démarrage du serveur demandé par {user}**\n⏰ Veuillez patienter pendant l'initialisation..."
    in_progress: "🟡 **Démarrage en cours...**\n📡 Magic Packet envoyé au serveur Proxmox\n⏱️ Temps estimé : 2-3 minutes"
    success: "🟢 **Serveur opérationnel !**\n🎮 Minecraft disponible sur {server_ip}:{port}\n✅ Prêt à jouer !"
    failed: "❌ **Échec du démarrage du serveur**\n⏰ Serveur non disponible après 10 minutes\n🔧 Vérifiez la configuration ou contactez l'admin"

  shutdown:
    initiated: "⏰ **Aucun utilisateur autorisé détecté**\n🕐 Arrêt du serveur dans {delay} minutes...\n👥 Rejoignez le salon vocal pour annuler"
    cancelled: "✅ **Arrêt annulé !**\n👋 {user} a rejoint le salon vocal\n🟢 Serveur maintenu en fonctionnement"
    in_progress: "🔴 **Arrêt du serveur en cours...**\n📡 Commande d'arrêt envoyée au serveur Proxmox\n⏱️ Temps estimé : 1 minute"
    confirmed: "⚫ **Serveur arrêté avec succès**\n💤 Serveur Proxmox éteint\n🔋 Économie d'énergie activée"

  admin_alerts:
    startup_failed: "🚨 **ALERTE ADMIN - Échec du démarrage**\n\n❌ Le serveur n'a pas pu démarrer après 10 minutes\n📊 Détails :\n   • Utilisateur : {user}\n   • Heure : {timestamp}\n   • Erreur : {error_details}\n\n🔧 Actions recommandées :\n   • Vérifier l'état du serveur Proxmox\n   • Contrôler la configuration Wake-on-LAN\n   • Vérifier les logs système"
```

---

## 🎯 **Bonnes pratiques**

### **1. Clarté des messages**

- Messages courts et précis
- Emojis pour faciliter la lecture
- Informations essentielles en premier

### **2. Cohérence**

- Même style pour tous les messages
- Variables standardisées
- Format uniforme

### **3. Informativité**

- Toujours indiquer l'action en cours
- Inclure les détails pertinents
- Proposer des actions si nécessaire

### **4. Gestion des erreurs**

- Messages d'erreur explicites
- Suggestions de résolution
- Escalade vers l'admin si critique

---

**Dernière mise à jour :** 2025-01-16  
**Version :** 1.1.0  
**Validation technique :** ✅ Vérifié avec sources officielles
