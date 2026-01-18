# Correction du problème Wake-on-LAN - Bot CubeGuardian

## Problème identifié

Le bot CubeGuardian envoyait bien le Magic Packet Wake-on-LAN selon les logs, mais le serveur ne démarrait pas. Le problème était dans l'implémentation du Wake-on-LAN qui utilisait uniquement le module `wakeonlan` Python.

## Solution implémentée

### 1. Version améliorée du module Wake-on-LAN

Le fichier `src/server_manager/wake_on_lan.py` a été amélioré avec :

- **Plusieurs méthodes d'envoi** : Module wakeonlan + Socket UDP brut
- **Plusieurs adresses de broadcast** : 255.255.255.255, 192.168.1.255, adresse IP directe
- **Plusieurs ports** : Port 9 et port 7
- **Logging détaillé** : Pour diagnostiquer les problèmes
- **Fallback robuste** : Si une méthode échoue, les autres sont tentées

### 2. Scripts de diagnostic créés

- `diagnostic-wol.py` : Diagnostic Python complet
- `diagnostic-wol.ps1` : Diagnostic PowerShell complet
- `test-wol-enhanced.py` : Test de la version améliorée
- `test-wol-comparison.ps1` : Comparaison avec wakemeonlan-x64
- `test-wol-quick.py` : Test rapide

## Comment tester la correction

### 1. Test rapide avec Python

```bash
cd Serveur_Docker/Bot-CubeGuardian
python test-wol-quick.py
```

### 2. Test complet avec PowerShell

```powershell
cd Serveur_Docker/Bot-CubeGuardian
.\test-wol-comparison.ps1
```

### 3. Test du bot complet

```bash
cd Serveur_Docker/Bot-CubeGuardian
python test-wol-enhanced.py
```

## Vérifications importantes

### Avant le test :

1. **Serveur éteint** : Vérifiez que le serveur Proxmox est bien éteint
2. **Wake-on-LAN activé** : Vérifiez dans le BIOS que le WOL est activé
3. **Carte réseau** : Vérifiez que la carte réseau supporte le WOL

### Pendant le test :

1. **Attendre 30-60 secondes** après l'envoi du paquet
2. **Observer le serveur** : LED, ventilateurs, bruits
3. **Vérifier la connectivité** : Ping vers 192.168.1.245

### Après le test :

1. **Vérifier Proxmox** : Interface web accessible sur https://192.168.1.245:8006
2. **Vérifier Minecraft** : Serveur accessible sur 192.168.1.105:25565

## Comparaison avec wakemeonlan-x64

Si `wakemeonlan-x64.exe` fonctionne mais pas le bot :

1. **Exécutez le test de comparaison** :

   ```powershell
   .\test-wol-comparison.ps1
   ```

2. **Comparez les résultats** entre les différentes méthodes

3. **Identifiez la méthode qui fonctionne** et ajustez le code si nécessaire

## Logs du bot

Avec la version améliorée, les logs montreront :

```
Wake-on-LAN réussi pour 192.168.1.245 (3 méthodes)
Magic Packet envoyé avec succès (3 méthodes)
```

Au lieu de :

```
Wake-on-LAN réussi pour 192.168.1.245
Magic Packet envoyé avec succès
```

## Dépannage

### Si le serveur ne démarre toujours pas :

1. **Vérifiez le BIOS** : Wake-on-LAN activé
2. **Vérifiez la carte réseau** : Support WOL activé
3. **Vérifiez le firewall** : Paquets UDP autorisés
4. **Testez avec wakemeonlan-x64** : Confirmez que le WOL fonctionne
5. **Vérifiez l'adresse MAC** : 00:23:7D:FD:C0:5C

### Si le bot ne détecte pas le démarrage :

1. **Vérifiez la connectivité** : Ping vers 192.168.1.245
2. **Vérifiez le port Proxmox** : 8006 accessible
3. **Vérifiez le port Minecraft** : 25565 accessible
4. **Augmentez le timeout** : Dans la configuration

## Configuration recommandée

Dans le fichier `.env`, assurez-vous que :

```env
# Serveur Proxmox
PROXMOX_HOST=192.168.1.245
PROXMOX_MAC=00:23:7D:FD:C0:5C

# Serveur Minecraft
MINECRAFT_HOST=192.168.1.105
MINECRAFT_PORT=25565

# Délais
STARTUP_TIMEOUT=600
CONNECTIVITY_CHECK_INTERVAL=10
```

## Résumé des améliorations

1. **Robustesse** : Plusieurs méthodes d'envoi
2. **Compatibilité** : Support de différents environnements réseau
3. **Diagnostic** : Logging détaillé pour le dépannage
4. **Fallback** : Si une méthode échoue, les autres sont tentées
5. **Test** : Scripts de test et de comparaison

La version améliorée devrait résoudre le problème de Wake-on-LAN et permettre au bot de démarrer correctement le serveur Proxmox.
