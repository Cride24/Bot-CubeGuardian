# 🔧 Modules Python Natifs - Bot CubeGuardian (Version Optimisée)

## 📋 **Vue d'ensemble**

Documentation complète des modules Python natifs pour le bot Discord CubeGuardian - **Version 2.0.0 avec API REST Proxmox** et workflows optimisés.

> ⚠️ **IMPORTANT :** Les scripts PowerShell sont maintenant **DÉPRÉCIÉS** dans la version 2.0.0. Le bot utilise maintenant l'API REST Proxmox pour l'arrêt du serveur.

**Sources officielles :**

- [Python Standard Library](https://docs.python.org/3/library/) - Version 3.11+
- [wakeonlan PyPI](https://pypi.org/project/wakeonlan/) - Wake-on-LAN natif
- [aiohttp PyPI](https://pypi.org/project/aiohttp/) - Client HTTP asynchrone
- [Proxmox API Docs](https://pve.proxmox.com/wiki/Proxmox_VE_API) - API REST Proxmox
- **Dernière vérification :** 2025-09-07

---

## 🎯 **Principe des modules Python natifs**

### **Migration depuis PowerShell vers Python**

| Aspect             | Scripts PowerShell  | Modules Python natifs |
| ------------------ | ------------------- | --------------------- |
| **Performance**    | Overhead subprocess | Exécution directe     |
| **Intégration**    | Appels externes     | Appels de fonctions   |
| **Gestion erreur** | Codes de retour     | Exception handling    |
| **Maintenance**    | Multi-langage       | Python unifié         |
| **Docker**         | Dépendances lourdes | Image légère          |

### **Avantages des modules Python natifs**

1. **✅ Performance** : Pas d'overhead PowerShell
2. **✅ Cohérence** : Tout le code en Python
3. **✅ Maintenance** : Un seul langage à maintenir
4. **✅ Docker** : Image plus légère et rapide
5. **✅ Tests** : Mocking Python standard
6. **✅ Debugging** : Stack traces natives

---

## 📁 **Structure des modules Python**

```
Serveur_Docker/Bot-CubeGuardian/
├── server_manager/
│   ├── __init__.py
│   ├── wake_on_lan.py          # Module Wake-on-LAN natif
│   ├── ssh_manager.py          # Module SSH et shutdown natif
│   ├── connectivity_checker.py # Module tests connectivité natif
│   ├── minecraft_checker.py    # Module vérification Minecraft natif
│   └── server_manager.py       # Module principal unifié
├── keys/
│   └── proxmox_key             # Clé SSH pour Proxmox
└── logs/
    ├── cubeguardian.log        # Logs principaux du bot (max 200 lignes)
    └── server_manager.log      # Logs des modules Python
```

---

## 🔧 **Module 1 : Wake-on-LAN**

### **Fichier : `wake_on_lan.py`**

#### **Classe principale**

```python
import asyncio
from wakeonlan import send_magic_packet
from typing import Dict, Any
import logging
from datetime import datetime

class WakeOnLANManager:
    """Gestionnaire Wake-on-LAN natif Python"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def wake_server(self, mac_address: str, target_host: str) -> Dict[str, Any]:
        """
        Envoie un Magic Packet Wake-on-LAN

        Args:
            mac_address: Adresse MAC du serveur (format: "00:23:7D:FD:C0:5C")
            target_host: Adresse IP du serveur (ex: "192.168.1.245")

        Returns:
            Dict avec success, message, timestamp, details
        """
```

#### **Fonctionnalités**

- ✅ Envoi de Magic Packet Wake-on-LAN natif
- ✅ Gestion d'erreur Python native
- ✅ Retour JSON structuré
- ✅ Logs détaillés avec logger Python
- ✅ Type hints pour meilleure maintenabilité

#### **Exemple de retour JSON**

```json
{
  "success": true,
  "message": "Magic Packet envoyé avec succès",
  "timestamp": "2025-01-16 14:30:00",
  "details": {
    "mac_address": "00:23:7D:FD:C0:5C",
    "target_host": "192.168.1.245",
    "packets_sent": 3,
    "operation": "wake_on_lan"
  }
}
```

#### **Gestion d'erreur**

- **Exception handling** : Try/catch Python natif
- **Logging** : Logger Python standard
- **Type safety** : Type hints pour validation

---

## 🔧 **Module 2 : SSH Manager**

### **Fichier : `ssh_manager.py`**

#### **Classe principale**

```python
import asyncio
import paramiko
from typing import Dict, Any
import logging
from datetime import datetime

class SSHManager:
    """Gestionnaire SSH natif Python"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def shutdown_server(self, target_host: str, ssh_user: str, ssh_key_path: str, delay_minutes: int = 0) -> Dict[str, Any]:
        """
        Arrête le serveur via SSH

        Args:
            target_host: Adresse IP du serveur
            ssh_user: Utilisateur SSH (ex: "root")
            ssh_key_path: Chemin vers la clé SSH privée
            delay_minutes: Délai avant arrêt (0 = immédiat)

        Returns:
            Dict avec success, message, timestamp, details
        """
```

#### **Fonctionnalités**

- ✅ Arrêt du serveur Proxmox via SSH natif
- ✅ Authentification par clé SSH avec paramiko
- ✅ Délai d'arrêt configurable
- ✅ Gestion d'erreur Python native
- ✅ Retour JSON structuré

#### **Exemple de retour JSON**

```json
{
  "success": true,
  "message": "Commande d'arrêt envoyée avec succès",
  "timestamp": "2025-01-16 14:30:00",
  "details": {
    "target_host": "192.168.1.245",
    "delay_minutes": 0,
    "operation": "shutdown"
  }
}
```

#### **Gestion d'erreur**

- **Exception handling** : Try/catch Python natif
- **SSH errors** : Gestion spécifique des erreurs paramiko
- **Timeout** : Gestion des timeouts de connexion

---

## 🔧 **Module 3 : Connectivity Checker**

### **Fichier : `connectivity_checker.py`**

#### **Classe principale**

```python
import asyncio
import subprocess
from typing import Dict, Any
import logging
from datetime import datetime

class ConnectivityChecker:
    """Vérificateur de connectivité natif Python"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def check_proxmox_connectivity(self, target_host: str, timeout_seconds: int = 10) -> Dict[str, Any]:
        """
        Vérifie la connectivité Proxmox (ping)

        Args:
            target_host: Adresse IP du serveur Proxmox
            timeout_seconds: Timeout en secondes

        Returns:
            Dict avec success, message, timestamp, details
        """
```

#### **Fonctionnalités**

- ✅ Test de connectivité Proxmox (ping) natif
- ✅ Timeout configurable
- ✅ Gestion d'erreur Python native
- ✅ Retour JSON structuré

#### **Exemple de retour JSON**

```json
{
  "success": true,
  "message": "Serveur Proxmox accessible",
  "timestamp": "2025-01-16 14:30:00",
  "details": {
    "target_host": "192.168.1.245",
    "response_time": "OK",
    "operation": "connectivity_check"
  }
}
```

#### **Gestion d'erreur**

- **Exception handling** : Try/catch Python natif
- **Subprocess** : Gestion asynchrone des processus
- **Timeout** : Gestion des timeouts de ping

---

## 🔧 **Module 4 : Minecraft Checker**

### **Fichier : `minecraft_checker.py`**

#### **Classe principale**

```python
import asyncio
import socket
from typing import Dict, Any
import logging
from datetime import datetime

class MinecraftChecker:
    """Vérificateur Minecraft natif Python"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def check_minecraft_connectivity(self, target_host: str, port: int = 25565, timeout_seconds: int = 5) -> Dict[str, Any]:
        """
        Vérifie la connectivité du serveur Minecraft

        Args:
            target_host: Adresse IP du serveur Minecraft
            port: Port Minecraft (défaut: 25565)
            timeout_seconds: Timeout en secondes

        Returns:
            Dict avec success, message, timestamp, details
        """
```

#### **Fonctionnalités**

- ✅ Test de connectivité TCP natif sur le port Minecraft
- ✅ Port configurable
- ✅ Timeout configurable
- ✅ Gestion d'erreur Python native
- ✅ Retour JSON structuré

#### **Exemple de retour JSON**

```json
{
  "success": true,
  "message": "Serveur Minecraft accessible",
  "timestamp": "2025-01-16 14:30:00",
  "details": {
    "target_host": "192.168.1.245",
    "port": 25565,
    "operation": "minecraft_check"
  }
}
```

#### **Gestion d'erreur**

- **Exception handling** : Try/catch Python natif
- **Socket errors** : Gestion spécifique des erreurs de socket
- **Timeout** : Gestion des timeouts de connexion TCP

---

## 🔄 **Intégration avec le bot**

### **ServerManager unifié**

```python
import asyncio
from typing import Dict, Any
import logging
from .wake_on_lan import WakeOnLANManager
from .ssh_manager import SSHManager
from .connectivity_checker import ConnectivityChecker
from .minecraft_checker import MinecraftChecker

class ServerManager:
    """Gestionnaire de serveurs unifié - Version Python natif"""

    def __init__(self, config: dict, logger: logging.Logger):
        self.config = config
        self.logger = logger

        # Initialisation des sous-modules
        self.wake_on_lan = WakeOnLANManager(logger)
        self.ssh_manager = SSHManager(logger)
        self.connectivity_checker = ConnectivityChecker(logger)
        self.minecraft_checker = MinecraftChecker(logger)

    async def wake_server(self, mac_address: str = None, target_host: str = None) -> Dict[str, Any]:
        """Wake-on-LAN du serveur Proxmox"""
        mac_address = mac_address or self.config['proxmox']['mac_address']
        target_host = target_host or self.config['proxmox']['ipv4']

        return await self.wake_on_lan.wake_server(mac_address, target_host)

    async def shutdown_server(self, target_host: str = None, ssh_user: str = None, ssh_key_path: str = None, delay_minutes: int = 0) -> Dict[str, Any]:
        """Arrêt du serveur Proxmox"""
        target_host = target_host or self.config['proxmox']['ipv4']
        ssh_user = ssh_user or self.config['proxmox']['ssh_user']
        ssh_key_path = ssh_key_path or self.config['proxmox']['ssh_key_path']

        return await self.ssh_manager.shutdown_server(target_host, ssh_user, ssh_key_path, delay_minutes)

    async def check_proxmox_status(self, target_host: str = None) -> Dict[str, Any]:
        """Vérification de la connectivité Proxmox"""
        target_host = target_host or self.config['proxmox']['ipv4']

        return await self.connectivity_checker.check_proxmox_connectivity(target_host)

    async def check_minecraft_status(self, target_host: str = None, port: int = None) -> Dict[str, Any]:
        """Vérification de la connectivité Minecraft"""
        target_host = target_host or self.config['minecraft']['ipv4']
        port = port or self.config['minecraft']['port']

        return await self.minecraft_checker.check_minecraft_connectivity(target_host, port)
```

### **Nouvelles dépendances Python**

```python
# requirements.txt - Version Python natif
discord.py>=2.6.3    # Version stable actuelle (2025)
pyyaml>=6.0
python-dotenv>=1.0.0
wakeonlan>=3.0.0     # Wake-on-LAN natif Python
paramiko>=3.4.0      # SSH client Python natif
asyncio-subprocess>=0.1.0  # Subprocess asynchrone
psutil>=5.9.0        # System monitoring

# Sources des versions :
# wakeonlan : https://pypi.org/project/wakeonlan/
# paramiko : https://pypi.org/project/paramiko/
# Dernière vérification : 2025-01-16
```

---

## 📊 **Gestion des erreurs**

### **Exception handling Python natif**

| Type d'erreur         | Description         | Action recommandée           |
| --------------------- | ------------------- | ---------------------------- |
| **Success**           | Opération réussie   | Aucune action                |
| **ConnectionError**   | Erreur de connexion | Vérifier la connectivité     |
| **TimeoutError**      | Timeout d'opération | Augmenter le délai d'attente |
| **SSHException**      | Erreur SSH          | Vérifier les permissions SSH |
| **FileNotFoundError** | Fichier manquant    | Vérifier la configuration    |

### **Gestion d'erreur dans le bot**

```python
async def handle_module_result(self, result: Dict[str, Any], operation: str):
    """Gère le résultat d'un module Python natif"""
    if result['success']:
        self.logger.info(f"Module {operation} réussi: {result['message']}")
        return True
    else:
        error_message = result.get('error', 'Erreur inconnue')
        self.logger.error(f"Module {operation} échoué: {error_message}")

        # Gestion spécifique par type d'erreur
        if "timeout" in error_message.lower():
            await self.send_admin_alert("timeout_error", {
                "operation": operation,
                "error_message": error_message
            })
        elif "ssh" in error_message.lower():
            await self.send_admin_alert("ssh_error", {
                "operation": operation,
                "error_message": error_message
            })

        return False
```

---

## 🧪 **Tests et validation**

### **Tests unitaires**

```python
import pytest
from unittest.mock import Mock, patch

class TestPowerShellScripts:
    """Tests pour les scripts PowerShell"""

    @pytest.mark.asyncio
    async def test_wake_server_success(self):
        """Test du wake-on-LAN réussi"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps({
                "success": True,
                "message": "Magic Packet envoyé avec succès"
            })

            result = await self.powershell_wrapper.wake_server("00:23:7D:FD:C0:5C", "192.168.1.245")

            assert result['success'] == True
            assert result['data']['message'] == "Magic Packet envoyé avec succès"

    @pytest.mark.asyncio
    async def test_wake_server_failure(self):
        """Test du wake-on-LAN échoué"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 2
            mock_run.return_value.stderr = "Erreur réseau"

            result = await self.powershell_wrapper.wake_server("00:23:7D:FD:C0:5C", "192.168.1.245")

            assert result['success'] == False
            assert result['returncode'] == 2
```

### **Tests d'intégration**

```python
class TestScriptIntegration:
    """Tests d'intégration des scripts"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test du workflow complet avec les scripts"""
        # 1. Wake-on-LAN
        wake_result = await self.powershell_wrapper.wake_server("00:23:7D:FD:C0:5C", "192.168.1.245")
        assert wake_result['success'] == True

        # 2. Vérification Proxmox
        proxmox_result = await self.powershell_wrapper.check_proxmox_connectivity("192.168.1.245")
        assert proxmox_result['success'] == True

        # 3. Vérification Minecraft
        minecraft_result = await self.powershell_wrapper.check_minecraft_connectivity("192.168.1.245", 25565)
        assert minecraft_result['success'] == True

        # 4. Shutdown
        shutdown_result = await self.powershell_wrapper.shutdown_server("192.168.1.245", "root", "./keys/proxmox_key")
        assert shutdown_result['success'] == True
```

---

## 🔒 **Sécurité**

### **Bonnes pratiques**

1. **✅ Clés SSH** : Stockage sécurisé des clés SSH
2. **✅ Permissions** : Scripts avec permissions minimales
3. **✅ Validation** : Validation des paramètres d'entrée
4. **✅ Logs** : Pas de données sensibles dans les logs
5. **✅ Isolation** : Exécution dans un environnement isolé

### **Gestion des secrets**

```python
class SecretManager:
    """Gestionnaire des secrets pour les scripts"""

    def __init__(self):
        self.ssh_key_path = os.getenv('SSH_KEY_PATH', './keys/proxmox_key')
        self.proxmox_password = os.getenv('PROXMOX_PASSWORD')

    def get_ssh_key_path(self) -> str:
        """Retourne le chemin de la clé SSH"""
        if not os.path.exists(self.ssh_key_path):
            raise FileNotFoundError(f"Clé SSH non trouvée: {self.ssh_key_path}")
        return self.ssh_key_path
```

---

## 📊 **Gestion des logs**

### **Rotation automatique des logs**

Le système de logs du bot implémente une **rotation automatique par nombre de lignes** :

#### **Configuration**

```yaml
logging:
  max_lines: 200 # Limite de 200 lignes par fichier
  rotation_enabled: true # Rotation automatique activée
  keep_oldest: false # Supprimer les lignes les plus anciennes
```

#### **Fonctionnement**

1. **Surveillance** : Le système surveille le nombre de lignes dans le fichier de log
2. **Déclenchement** : Quand 200 lignes sont atteintes, la rotation se déclenche
3. **Rotation** : Les lignes les plus anciennes sont supprimées
4. **Conservation** : Seules les 100 lignes les plus récentes sont conservées
5. **Continuation** : Les nouveaux logs s'ajoutent normalement

#### **Exemple de rotation**

```
Avant rotation : 200 lignes
├── Ligne 1 (ancienne)
├── Ligne 2 (ancienne)
├── ...
├── Ligne 100 (ancienne)
├── Ligne 101 (récente) ← Conservation à partir d'ici
├── ...
└── Ligne 200 (récente)

Après rotation : 100 lignes
├── Ligne 101 (récente)
├── Ligne 102 (récente)
├── ...
└── Ligne 200 (récente)

Nouveau log : Ligne 201 (nouvelle)
```

#### **Avantages**

- **✅ Taille contrôlée** : Fichier de log toujours < 200 lignes
- **✅ Performance** : Pas de ralentissement avec de gros fichiers
- **✅ Historique récent** : Conservation des logs les plus pertinents
- **✅ Automatique** : Aucune intervention manuelle requise

#### **Logs de rotation**

```
2025-01-16 14:30:00 - CubeGuardian - INFO - Rotation des logs effectuée: 200 -> 100 lignes
2025-01-16 15:45:00 - CubeGuardian - INFO - Rotation des logs effectuée: 200 -> 100 lignes
```

---

## 📋 **Checklist de déploiement**

### **Prérequis**

- [ ] Python 3.11+ installé
- [ ] Packages Python installés (wakeonlan, paramiko)
- [ ] Clé SSH Proxmox configurée
- [ ] Permissions d'accès aux modules
- [ ] Variables d'environnement définies

### **Validation**

- [ ] Modules Python importables sans erreur
- [ ] Retour JSON valide
- [ ] Exception handling fonctionnel
- [ ] Gestion d'erreur fonctionnelle
- [ ] Logs générés correctement

### **Tests**

- [ ] Test wake-on-LAN natif
- [ ] Test shutdown SSH natif
- [ ] Test vérification Proxmox natif
- [ ] Test vérification Minecraft natif
- [ ] Test gestion d'erreur Python

---

**Dernière mise à jour :** 2025-01-16  
**Version :** 2.0.0 - **Migration Python natif**  
**Validation technique :** ✅ Vérifié avec sources officielles
