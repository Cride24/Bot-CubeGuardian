# 🤖 Bot Discord CubeGuardian - Cahier des Charges

## 📋 **Vue d'ensemble**

**Nom du projet :** CubeGuardian  
**Type :** Bot Discord automatisé  
**Objectif :** Surveillance et gestion automatique du serveur Proxmox/Minecraft basée sur l'activité vocale Discord

---

## 🎯 **Objectifs du projet**

### **Objectif principal**

Automatiser le démarrage et l'arrêt du serveur Proxmox (et du serveur Minecraft) en fonction de la présence d'utilisateurs autorisés dans un salon vocal Discord spécifique.

### **Objectifs secondaires**

- ✅ Réduction de la consommation électrique
- ✅ Automatisation complète du processus
- ✅ Notifications en temps réel des actions
- ✅ Gestion des utilisateurs autorisés
- ✅ Surveillance de la disponibilité des services

---

## 📁 **Structure du cahier des charges**

- **[01-Workflow-Complet.md](01-Workflow-Complet.md)** - Workflow détaillé avec tous les cas
- **[02-Configuration.md](02-Configuration.md)** - Paramètres et fichiers de config
- **[03-Specifications-Techniques.md](03-Specifications-Techniques.md)** - Détails techniques
- **[04-Messages-Et-Notifications.md](04-Messages-Et-Notifications.md)** - Messages du bot
- **[05-Cas-D-Usage.md](05-Cas-D-Usage.md)** - Scénarios d'utilisation
- **[06-Architecture.md](06-Architecture.md)** - Architecture du système
- **[07-Scripts-PowerShell.md](07-Scripts-PowerShell.md)** - Scripts PowerShell adaptés au bot
- **[08-Bonnes-Pratiques-Discord.md](08-Bonnes-Pratiques-Discord.md)** - Bonnes pratiques Discord 2025

---

## 🚀 **Fonctionnalités principales**

### **1. Surveillance vocale**

- Détection des connexions/déconnexions dans le salon vocal
- Vérification des identités autorisées
- Gestion des timers d'arrêt

### **2. Gestion du serveur**

- Wake-on-LAN du serveur Proxmox
- Surveillance de la disponibilité Minecraft
- Arrêt propre du serveur Proxmox

### **3. Commandes interactives**

- Commande de redémarrage Minecraft par message
- Reconnaissance de langage naturel en français
- Restriction aux joueurs autorisés seulement
- Support mentions (@bot) et messages privés

### **4. Notifications**

- Messages dans le salon textuel
- Messages privés à l'admin en cas de problème
- Logs détaillés des actions

### **5. Configuration**

- Fichier de configuration centralisé
- Gestion des utilisateurs autorisés
- Paramètres personnalisables

---

## 📊 **Métriques de succès**

- ✅ **Disponibilité :** Bot opérationnel 24/7
- ✅ **Réactivité :** Détection immédiate des connexions
- ✅ **Fiabilité :** Gestion des cas d'erreur
- ✅ **Transparence :** Notifications claires des actions

---

## 🔧 **Technologies utilisées**

- **Langage :** Python 3.11+ ([python.org](https://www.python.org/downloads/))
- **Bibliothèque Discord :** discord.py 2.6.3+ ([PyPI](https://pypi.org/project/discord.py/))
- **API Discord :** v10 ([Discord API Docs](https://discord.com/developers/docs/))
- **Scripts système :** PowerShell 5.1+ ([Microsoft Docs](https://docs.microsoft.com/powershell/))
- **Configuration :** YAML/JSON avec gestion sécurisée des secrets
- **Logs :** Fichiers texte + Discord (rotation automatique à 200 lignes)
- **Sécurité :** Rate limiting, permissions minimales, chiffrement des secrets
- **Déploiement :** Docker 20.10+ ([Docker Docs](https://docs.docker.com/))

**Sources vérifiées le :** 2025-01-16

---

## 📅 **Planning de développement**

### **Phase 1 : Développement local**

- [ ] Structure de base du bot
- [ ] Surveillance des salons vocaux
- [ ] Intégration des scripts PowerShell
- [ ] Tests en local

### **Phase 2 : Optimisation**

- [ ] Gestion d'erreurs avancée
- [ ] Logs détaillés
- [ ] Configuration avancée
- [ ] Tests de charge

### **Phase 3 : Déploiement**

- [ ] Containerisation Docker
- [ ] Déploiement sur serveur
- [ ] Monitoring et maintenance
- [ ] Documentation utilisateur

---

---

## 🆕 **Nouvelles fonctionnalités (Version 2.0.0)**

### **✨ Workflows optimisés**

- **Démarrage intelligent** : Test immédiat Minecraft avant démarrage
- **Arrêt propre** : Arrêt des conteneurs LXC avant le nœud Proxmox
- **Surveillance améliorée** : Tests toutes les minutes avec timeouts appropriés
- **Timer avec interruption** : Possibilité d'annuler l'arrêt

### **✨ Améliorations techniques**

- **API REST Proxmox** : Remplacement des scripts PowerShell par l'API REST
- **Tests TCP** : Remplacement du ping par des tests de ports
- **Gestion d'erreurs robuste** : Logs détaillés et récupération d'erreurs
- **Docker optimisé** : Configuration réseau host et capabilities

### **✨ Expérience utilisateur**

- **Messages informatifs** : Compte à rebours et statut détaillé
- **Détection "déjà opérationnel"** : Évite les démarrages inutiles
- **Notifications en temps réel** : Information continue sur l'état du serveur

### **✨ Commandes interactives (Version 2.1.0)**

- **Redémarrage par commande** : Commande "@bot redémarrer le serveur minecraft"
- **Reconnaissance naturelle** : Support français avec fautes d'orthographe et anglicismes
- **Sécurité renforcée** : Cooldown, confirmation, validation utilisateur
- **API REST LXC** : Redémarrage direct du conteneur Minecraft via API Proxmox

---

**Dernière mise à jour :** 2025-01-16  
**Version :** 2.1.0 (Commandes Interactives)  
**Statut :** En développement  
**Validation technique :** ✅ Workflows optimisés validés, 🔄 Commandes interactives en cours
