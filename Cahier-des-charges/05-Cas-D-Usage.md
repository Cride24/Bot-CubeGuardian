# 🎯 Cas d'Usage - Bot CubeGuardian

## 📋 **Vue d'ensemble**

Scénarios d'utilisation détaillés du bot Discord CubeGuardian dans différentes situations.

---

## 🎮 **Scénarios principaux**

### **Scénario 1 : Session de jeu normale**

#### **Contexte**

- Serveur Proxmox arrêté
- Serveur Minecraft indisponible
- Utilisateur autorisé veut jouer

#### **Déroulement**

```
1. 👋 Player1 rejoint "L'écho-du-Cube"
   → Bot : "👋 Player1 a rejoint le salon vocal"

2. 🟡 Demande de démarrage
   → Bot : "🟡 Démarrage du serveur demandé par Player1"

3. 📡 Wake-on-LAN envoyé
   → Bot : "🟡 Démarrage en cours... Magic Packet envoyé"

4. ⏱️ Surveillance (10 minutes)
   → Bot : "👁️ Surveillance du démarrage active"

5. 🟢 Serveur opérationnel
   → Bot : "🟢 Serveur opérationnel ! Minecraft disponible sur 192.168.1.245:25565"

6. 🎮 Player1 peut jouer
```

#### **Résultat attendu**

- Serveur Proxmox démarré
- Serveur Minecraft disponible
- Player1 peut se connecter au jeu

---

### **Scénario 2 : Fin de session avec arrêt automatique**

#### **Contexte**

- Serveur opérationnel
- Player1 est le dernier utilisateur autorisé
- Player1 quitte le salon vocal

#### **Déroulement**

```
1. 👋 Player1 quitte "L'écho-du-Cube"
   → Bot : "👋 Player1 a quitté le salon vocal"

2. ⏰ Timer d'arrêt lancé (10 minutes)
   → Bot : "⏰ Aucun utilisateur autorisé détecté. Arrêt dans 10 minutes..."

3. ⏱️ Attente (10 minutes)
   → Bot : "⏱️ Timer d'arrêt actif. Temps restant : 7 minutes"

4. 🔴 Arrêt du serveur
   → Bot : "🔴 Arrêt du serveur en cours..."

5. ⚫ Confirmation d'arrêt
   → Bot : "⚫ Serveur arrêté avec succès"
```

#### **Résultat attendu**

- Serveur Proxmox arrêté
- Économie d'énergie
- Bot retourne en mode surveillance

---

### **Scénario 3 : Annulation d'arrêt**

#### **Contexte**

- Timer d'arrêt actif (5 minutes restantes)
- Player2 rejoint le salon vocal

#### **Déroulement**

```
1. ⏰ Timer d'arrêt actif
   → Bot : "⏱️ Timer d'arrêt actif. Temps restant : 5 minutes"

2. 👋 Player2 rejoint "L'écho-du-Cube"
   → Bot : "👋 Player2 a rejoint le salon vocal"

3. ✅ Annulation de l'arrêt
   → Bot : "✅ Arrêt annulé ! Player2 a rejoint le salon vocal"

4. 🟢 Serveur maintenu
   → Bot : "🟢 Serveur maintenu en fonctionnement"
```

#### **Résultat attendu**

- Timer d'arrêt annulé
- Serveur maintenu en fonctionnement
- Player2 peut jouer immédiatement

---

## 🚨 **Scénarios d'erreur**

### **Scénario 4 : Échec du démarrage**

#### **Contexte**

- Player1 rejoint le salon vocal
- Wake-on-LAN envoyé
- Serveur ne démarre pas dans les 5 minutes

#### **Déroulement**

```
1. 🟡 Demande de démarrage
   → Bot : "🟡 Démarrage du serveur demandé par Player1"

2. 📡 Wake-on-LAN envoyé
   → Bot : "🟡 Démarrage en cours..."

3. ⏱️ Surveillance (10 minutes)
   → Bot : "👁️ Surveillance du démarrage active"

4. ❌ Échec du démarrage
   → Bot : "❌ Échec du démarrage du serveur. Serveur non disponible après 10 minutes"

5. 🚨 Alerte admin (privée)
   → Admin : "🚨 ALERTE ADMIN - Échec du démarrage. Le serveur n'a pas pu démarrer..."
```

#### **Actions de récupération**

- Vérification manuelle du serveur
- Redémarrage manuel si nécessaire
- Vérification de la configuration Wake-on-LAN

---

### **Scénario 5 : Échec de l'arrêt**

#### **Contexte**

- Timer d'arrêt expiré
- Commande shutdown envoyée
- Serveur ne s'arrête pas

#### **Déroulement**

```
1. 🔴 Arrêt du serveur
   → Bot : "🔴 Arrêt du serveur en cours..."

2. ⏱️ Attente de confirmation (1 minute)
   → Bot : "⏱️ Attente de confirmation d'arrêt..."

3. ❌ Échec de l'arrêt
   → Bot : "❌ Échec de l'arrêt du serveur. Le serveur n'a pas répondu"

4. 🚨 Alerte admin (privée)
   → Admin : "🚨 ALERTE ADMIN - Échec de l'arrêt. Intervention manuelle requise"
```

#### **Actions de récupération**

- Arrêt manuel du serveur
- Vérification de la connectivité SSH
- Redémarrage du bot si nécessaire

---

### **Scénario 6 : Perte de connectivité**

#### **Contexte**

- Bot en fonctionnement normal
- Problème réseau temporaire
- Bot ne peut plus communiquer avec le serveur

#### **Déroulement**

```
1. 🔌 Problème de connectivité
   → Bot : "🔌 Problème de connectivité détecté"

2. 🔄 Tentatives de reconnexion
   → Bot : "🔄 Tentative de reconnexion en cours..."

3. ✅ Connectivité rétablie
   → Bot : "✅ Connectivité rétablie. Surveillance normale reprise"

OU

4. 🚨 Alerte admin (si échec)
   → Admin : "🚨 ALERTE ADMIN - Perte de connectivité. Le bot ne peut plus communiquer..."
```

---

## 👥 **Scénarios multi-utilisateurs**

### **Scénario 7 : Session multi-joueurs**

#### **Contexte**

- Serveur opérationnel
- Player1 déjà connecté
- Player2 rejoint le salon vocal

#### **Déroulement**

```
1. 🎮 Player1 joue (serveur déjà opérationnel)
   → Bot : "🟢 Serveur opérationnel !"

2. 👋 Player2 rejoint "L'écho-du-Cube"
   → Bot : "👋 Player2 a rejoint le salon vocal"

3. 👥 Mise à jour du compteur
   → Bot : "👥 2 utilisateur(s) autorisé(s) présent(s)"
```

#### **Résultat attendu**

- Aucune action sur le serveur (déjà opérationnel)
- Compteur d'utilisateurs mis à jour
- Player2 peut jouer immédiatement

---

### **Scénario 8 : Départ échelonné des joueurs**

#### **Contexte**

- 3 joueurs autorisés présents
- Player1 quitte, puis Player2, puis Player3

#### **Déroulement**

```
1. 👋 Player1 quitte
   → Bot : "👋 Player1 a quitté le salon vocal"
   → Bot : "👥 2 utilisateur(s) autorisé(s) restant(s)"

2. 👋 Player2 quitte
   → Bot : "👋 Player2 a quitté le salon vocal"
   → Bot : "👥 1 utilisateur(s) autorisé(s) restant(s)"

3. 👋 Player3 quitte (dernier utilisateur)
   → Bot : "👋 Player3 a quitté le salon vocal"
   → Bot : "⏰ Aucun utilisateur autorisé détecté. Arrêt dans 10 minutes..."
```

#### **Résultat attendu**

- Timer d'arrêt lancé seulement quand le dernier utilisateur quitte
- Serveur maintenu tant qu'il y a des utilisateurs autorisés

---

## 🚫 **Scénarios d'accès refusé**

### **Scénario 9 : Utilisateur non autorisé**

#### **Contexte**

- Utilisateur non autorisé rejoint le salon vocal
- Bot détecte l'utilisateur non autorisé

#### **Déroulement**

```
1. 👋 UnknownUser rejoint "L'écho-du-Cube"
   → Bot : "👋 UnknownUser a rejoint le salon vocal"

2. 🚫 Vérification d'autorisation
   → Bot : "🚫 Accès refusé. UnknownUser n'est pas autorisé à utiliser ce bot"

3. 📋 Information
   → Bot : "📋 Contactez l'admin pour obtenir l'accès"
```

#### **Résultat attendu**

- Aucune action sur le serveur
- Message d'information pour l'utilisateur
- Log de l'événement pour l'admin

---

## 🔧 **Scénarios de maintenance**

### **Scénario 10 : Mode maintenance**

#### **Contexte**

- Admin active le mode maintenance
- Bot suspend temporairement la surveillance

#### **Déroulement**

```
1. 🔧 Activation du mode maintenance
   → Bot : "🔧 Mode maintenance activé. Surveillance temporairement suspendue"

2. ⏸️ Suspension de la surveillance
   → Bot : "📋 Raison : Mise à jour du serveur"

3. ✅ Fin de la maintenance
   → Bot : "✅ Mode maintenance désactivé. Surveillance reprise"
```

#### **Résultat attendu**

- Surveillance suspendue pendant la maintenance
- Aucune action automatique sur le serveur
- Reprise normale après maintenance

---

## 📊 **Scénarios de monitoring**

### **Scénario 11 : Rapport de statistiques**

#### **Contexte**

- Fin de journée
- Bot génère un rapport automatique

#### **Déroulement**

```
1. 📊 Génération du rapport
   → Bot : "📊 Rapport quotidien - 2025-01-16"

2. 📈 Affichage des statistiques
   → Bot : "🟢 Démarrages réussis : 3
            ❌ Démarrages échoués : 0
            🔴 Arrêts réussis : 2
            👥 Utilisateurs actifs : 2
            ⏱️ Temps de fonctionnement : 4h 32min"
```

#### **Résultat attendu**

- Rapport détaillé des activités
- Statistiques de performance
- Informations pour l'optimisation

---

## 🎯 **Matrice de scénarios**

| Scénario                  | Utilisateurs        | État serveur        | Action bot         | Résultat               |
| ------------------------- | ------------------- | ------------------- | ------------------ | ---------------------- |
| **1. Session normale**    | 0→1                 | Arrêté→Opérationnel | Wake-on-LAN        | Serveur démarré        |
| **2. Fin de session**     | 1→0                 | Opérationnel→Arrêté | Shutdown           | Serveur arrêté         |
| **3. Annulation arrêt**   | 0→1 (pendant timer) | Opérationnel        | Annulation         | Serveur maintenu       |
| **4. Échec démarrage**    | 0→1                 | Arrêté              | Wake-on-LAN échoue | Alerte admin           |
| **5. Échec arrêt**        | 1→0                 | Opérationnel        | Shutdown échoue    | Alerte admin           |
| **6. Perte connectivité** | Variable            | Variable            | Reconnexion        | Récupération           |
| **7. Multi-joueurs**      | 1→2                 | Opérationnel        | Aucune             | Compteur mis à jour    |
| **8. Départ échelonné**   | 3→2→1→0             | Opérationnel→Arrêté | Shutdown           | Serveur arrêté         |
| **9. Non autorisé**       | 0→1 (non autorisé)  | Variable            | Aucune             | Message refus          |
| **10. Maintenance**       | Variable            | Variable            | Suspension         | Surveillance suspendue |
| **11. Rapport**           | Variable            | Variable            | Génération         | Statistiques           |

---

## 🔄 **Flux de décision**

### **Arbre de décision principal**

```
Utilisateur rejoint le salon vocal
    ↓
Est-il autorisé ?
    ↓ OUI                    ↓ NON
Vérifier l'état du serveur   Ignorer l'utilisateur
    ↓
Serveur arrêté ?
    ↓ OUI                    ↓ NON
Envoyer Wake-on-LAN          Aucune action
    ↓
Surveiller le démarrage
    ↓
Serveur opérationnel ?
    ↓ OUI                    ↓ NON
Notifier le succès          Alerter l'admin
```

### **Arbre de décision d'arrêt**

```
Utilisateur quitte le salon vocal
    ↓
D'autres utilisateurs autorisés présents ?
    ↓ OUI                    ↓ NON
Mettre à jour le compteur    Lancer le timer d'arrêt
    ↓
Timer d'arrêt actif
    ↓
Utilisateur autorisé rejoint ?
    ↓ OUI                    ↓ NON
Annuler l'arrêt              Continuer le timer
    ↓
Timer expiré ?
    ↓ OUI                    ↓ NON
Envoyer shutdown             Continuer l'attente
    ↓
Surveiller l'arrêt
    ↓
Arrêt confirmé ?
    ↓ OUI                    ↓ NON
Notifier le succès          Alerter l'admin
```

---

## 📋 **Checklist de validation**

### **Tests de scénarios**

- [ ] **Scénario 1** : Session de jeu normale
- [ ] **Scénario 2** : Fin de session avec arrêt automatique
- [ ] **Scénario 3** : Annulation d'arrêt
- [ ] **Scénario 4** : Échec du démarrage
- [ ] **Scénario 5** : Échec de l'arrêt
- [ ] **Scénario 6** : Perte de connectivité
- [ ] **Scénario 7** : Session multi-joueurs
- [ ] **Scénario 8** : Départ échelonné des joueurs
- [ ] **Scénario 9** : Utilisateur non autorisé
- [ ] **Scénario 10** : Mode maintenance
- [ ] **Scénario 11** : Rapport de statistiques

### **Critères de validation**

- [ ] Messages appropriés affichés
- [ ] Actions correctes exécutées
- [ ] Gestion d'erreur fonctionnelle
- [ ] Notifications admin envoyées
- [ ] Logs correctement enregistrés
- [ ] Performance acceptable
- [ ] Sécurité respectée

---

**Dernière mise à jour :** 2025-01-16  
**Version :** 1.1.0  
**Validation technique :** ✅ Vérifié avec sources officielles
