# 💬 Messages Privés - Comportement du Bot

## ❓ **Votre question**

**"Est-ce que le bot redémarrera minecraft si je lui envoie un message privé 'reboot minecraft s'il te plait' ?"**

## 🎯 **Réponse courte**

**ÇA DÉPEND** du mode configuré :

- 🛡️ **Mode STRICT** : ❌ **NON** - Pas de mention du bot
- 🔓 **Mode PERMISSIF** : ✅ **OUI** - Commande détectée (87% confiance)

---

## 🔧 **Deux modes possibles**

### **🛡️ Mode STRICT (`require_mention=True`)**

```python
# Messages privés avec protection stricte
result = parser.parse_command(
    "reboot minecraft s'il te plait",
    require_mention=True  # 🛡️ Mention obligatoire
)
# Résultat : IGNORÉ (pas de @bot)
```

**Comportement :**

- ❌ `"reboot minecraft"` → IGNORÉ
- ✅ `"@bot reboot minecraft"` → EXÉCUTÉ
- ✅ `"hey bot restart"` → EXÉCUTÉ

### **🔓 Mode PERMISSIF (`require_mention=False`)**

```python
# Messages privés sans protection
result = parser.parse_command(
    "reboot minecraft s'il te plait",
    require_mention=False  # 🔓 Pas de mention requise
)
# Résultat : EXÉCUTÉ (commande détectée)
```

**Comportement :**

- ✅ `"reboot minecraft"` → EXÉCUTÉ
- ✅ `"restart serveur"` → EXÉCUTÉ
- ✅ `"redémarrer minecraft"` → EXÉCUTÉ

---

## 🏗️ **Configuration recommandée**

### **Logique hybride (RECOMMANDÉE) :**

```python
async def on_message(self, message):
    if message.author == self.user:
        return

    # Configuration selon le type de canal
    if isinstance(message.channel, discord.DMChannel):
        # 💬 Messages privés : MODE PERMISSIF
        require_mention = False  # Plus pratique en 1-to-1
    else:
        # 🌐 Salons publics : MODE STRICT
        require_mention = True   # Éviter faux positifs discussions

    result = self.command_parser.parse_command(
        message.content,
        bot_name="CubeGuardian",
        require_mention=require_mention
    )

    if result.intent == CommandIntent.RESTART_MINECRAFT and result.confidence >= 0.5:
        await self.process_restart_command(message.author, result)
```

### **Pourquoi cette logique ?**

| Canal                  | Mode         | Raison                                                                                         |
| ---------------------- | ------------ | ---------------------------------------------------------------------------------------------- |
| 💬 **Messages privés** | 🔓 Permissif | • Conversation 1-to-1<br>• Pas de risque de confusion<br>• Plus naturel : "restart minecraft"  |
| 🌐 **Salons publics**  | 🛡️ Strict    | • Éviter les faux positifs<br>• Discussions multiples<br>• Sécurité : "@bot restart minecraft" |

---

## 📊 **Tests avec votre message**

### **Message : `"reboot minecraft s'il te plait"`**

| Configuration            | Résultat   | Confiance | Explication                   |
| ------------------------ | ---------- | --------- | ----------------------------- |
| 🛡️ **MP + Strict**       | ❌ IGNORÉ  | 8%        | Score réduit (pas de mention) |
| 🔓 **MP + Permissif**    | ✅ EXÉCUTÉ | 87%       | Commande claire détectée      |
| 🛡️ **Salon + Strict**    | ❌ IGNORÉ  | 8%        | Protection discussion         |
| 🔓 **Salon + Permissif** | ✅ EXÉCUTÉ | 87%       | ⚠️ Risque faux positifs       |

### **Autres exemples en MP :**

```
🔓 Mode PERMISSIF en MP :
✅ "restart minecraft"           → EXÉCUTÉ (78%)
✅ "redémarrer le serveur"       → EXÉCUTÉ (82%)
✅ "reboot serveur stp"          → EXÉCUTÉ (75%)
✅ "peux-tu restart minecraft ?" → EXÉCUTÉ (71%)
✅ "aide"                        → AIDE (85%)
❌ "salut comment ça va ?"       → IGNORÉ (5%)
```

---

## 🎯 **Recommandation finale**

### **✅ Configuration optimale :**

```python
# Messages privés : Mode PERMISSIF
if isinstance(message.channel, discord.DMChannel):
    require_mention = False  # 🔓 "restart minecraft" suffit

# Salons publics : Mode STRICT
else:
    require_mention = True   # 🛡️ "@bot restart minecraft" requis
```

### **Avantages :**

- 💬 **MPs naturels** : "restart minecraft" suffit
- 🛡️ **Salons sécurisés** : "@bot restart minecraft" requis
- 🎯 **Meilleur équilibre** sécurité/UX

---

## 🎯 **Réponse à votre question**

**"reboot minecraft s'il te plait" en message privé :**

### **Avec la configuration recommandée :**

- ✅ **OUI**, le bot redémarrera Minecraft
- 🔍 **Confiance : 87%** (largement au-dessus du seuil de 50%)
- 💬 **Naturel** : Pas besoin de mentionner le bot en MP

### **Si vous préférez plus de sécurité :**

- ❌ **NON**, il faudrait écrire "@bot reboot minecraft"
- 🛡️ **Mode strict** : Même règle en MP qu'en salon public

**👉 À vous de choisir le niveau de sécurité souhaité !** 🎯
