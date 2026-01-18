# 🚀 Prompt Développeur - Refactorisation Module Gestion Serveurs

## 📋 **Contexte**

Le bot Discord CubeGuardian utilise actuellement des **scripts PowerShell** pour la gestion des serveurs (Wake-on-LAN, shutdown, vérifications). Cette approche pose des problèmes dans un environnement Docker Linux.

## 🎯 **Objectif**

**Refactoriser complètement le module de gestion des serveurs** pour utiliser du **Python natif** au lieu des scripts PowerShell.

## 🔧 **Tâches à réaliser**

### **1. Remplacer les scripts PowerShell par des modules Python**

#### **Scripts à remplacer :**

- `wakeup-pve-bot.ps1` → Module Python `wake_on_lan.py`
- `shutdown-pve-bot.ps1` → Module Python `ssh_manager.py`
- `check-proxmox-bot.ps1` → Module Python `connectivity_checker.py`
- `check-minecraft-bot.ps1` → Module Python `minecraft_checker.py`

### **2. Nouvelles dépendances Python à ajouter**

```python
# requirements.txt - Nouvelles dépendances
wakeonlan>=3.0.0          # Wake-on-LAN natif
paramiko>=3.4.0           # SSH client Python
asyncio-subprocess>=0.1.0 # Subprocess asynchrone
```

### **3. Architecture du nouveau module**

```python
# Structure proposée
server_manager/
├── __init__.py
├── wake_on_lan.py        # Gestion Wake-on-LAN
├── ssh_manager.py        # Gestion SSH et shutdown
├── connectivity_checker.py # Tests de connectivité
├── minecraft_checker.py  # Vérification Minecraft
└── server_manager.py     # Module principal unifié
```

## 📝 **Spécifications techniques**

### **1. Module Wake-on-LAN (`wake_on_lan.py`)**

```python
import asyncio
from wakeonlan import send_magic_packet
from typing import Dict, Any
import logging

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
        try:
            # Envoi du Magic Packet
            send_magic_packet(mac_address)

            result = {
                "success": True,
                "message": "Magic Packet envoyé avec succès",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "mac_address": mac_address,
                    "target_host": target_host,
                    "packets_sent": 3,
                    "operation": "wake_on_lan"
                }
            }

            self.logger.info(f"Wake-on-LAN réussi pour {target_host}")
            return result

        except Exception as e:
            result = {
                "success": False,
                "message": "Erreur lors de l'envoi du Magic Packet",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "details": {
                    "mac_address": mac_address,
                    "target_host": target_host,
                    "operation": "wake_on_lan"
                }
            }

            self.logger.error(f"Erreur Wake-on-LAN: {e}")
            return result
```

### **2. Module SSH Manager (`ssh_manager.py`)**

```python
import asyncio
import paramiko
from typing import Dict, Any
import logging

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
        try:
            # Connexion SSH
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Chargement de la clé privée
            private_key = paramiko.RSAKey.from_private_key_file(ssh_key_path)

            # Connexion
            ssh_client.connect(
                hostname=target_host,
                username=ssh_user,
                pkey=private_key,
                timeout=10
            )

            # Commande d'arrêt
            if delay_minutes > 0:
                command = f"shutdown -h +{delay_minutes}"
            else:
                command = "shutdown -h now"

            stdin, stdout, stderr = ssh_client.exec_command(command)

            # Attendre la fin de la commande
            exit_status = stdout.channel.recv_exit_status()
            ssh_client.close()

            if exit_status == 0:
                result = {
                    "success": True,
                    "message": "Commande d'arrêt envoyée avec succès",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "target_host": target_host,
                        "delay_minutes": delay_minutes,
                        "operation": "shutdown"
                    }
                }
                self.logger.info(f"Shutdown réussi pour {target_host}")
                return result
            else:
                raise Exception(f"Commande SSH échouée (code: {exit_status})")

        except Exception as e:
            result = {
                "success": False,
                "message": "Erreur lors de l'envoi de la commande d'arrêt",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "details": {
                    "target_host": target_host,
                    "operation": "shutdown"
                }
            }

            self.logger.error(f"Erreur SSH shutdown: {e}")
            return result
```

### **3. Module Connectivity Checker (`connectivity_checker.py`)**

```python
import asyncio
import socket
import subprocess
from typing import Dict, Any
import logging

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
        try:
            # Test de ping asynchrone
            process = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', str(timeout_seconds), target_host,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                result = {
                    "success": True,
                    "message": "Serveur Proxmox accessible",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "target_host": target_host,
                        "response_time": "OK",
                        "operation": "connectivity_check"
                    }
                }
                self.logger.info(f"Proxmox {target_host} accessible")
                return result
            else:
                result = {
                    "success": False,
                    "message": "Serveur Proxmox inaccessible",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "target_host": target_host,
                        "operation": "connectivity_check"
                    }
                }
                self.logger.warning(f"Proxmox {target_host} inaccessible")
                return result

        except Exception as e:
            result = {
                "success": False,
                "message": "Erreur lors de la vérification de connectivité",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "details": {
                    "target_host": target_host,
                    "operation": "connectivity_check"
                }
            }

            self.logger.error(f"Erreur connectivité Proxmox: {e}")
            return result
```

### **4. Module Minecraft Checker (`minecraft_checker.py`)**

```python
import asyncio
import socket
from typing import Dict, Any
import logging

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
        try:
            # Test de connectivité TCP asynchrone
            future = asyncio.open_connection(target_host, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout_seconds)

            # Fermeture de la connexion
            writer.close()
            await writer.wait_closed()

            result = {
                "success": True,
                "message": "Serveur Minecraft accessible",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "target_host": target_host,
                    "port": port,
                    "operation": "minecraft_check"
                }
            }

            self.logger.info(f"Minecraft {target_host}:{port} accessible")
            return result

        except asyncio.TimeoutError:
            result = {
                "success": False,
                "message": "Serveur Minecraft inaccessible (timeout)",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "target_host": target_host,
                    "port": port,
                    "operation": "minecraft_check"
                }
            }

            self.logger.warning(f"Minecraft {target_host}:{port} timeout")
            return result

        except Exception as e:
            result = {
                "success": False,
                "message": "Serveur Minecraft inaccessible",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "details": {
                    "target_host": target_host,
                    "port": port,
                    "operation": "minecraft_check"
                }
            }

            self.logger.error(f"Erreur connectivité Minecraft: {e}")
            return result
```

### **5. Module Principal Unifié (`server_manager.py`)**

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

    async def wait_for_startup(self, timeout: int = 600) -> bool:
        """Attend que le serveur soit disponible"""
        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Vérifier Proxmox
            proxmox_result = await self.check_proxmox_status()
            if proxmox_result['success']:
                # Vérifier Minecraft
                minecraft_result = await self.check_minecraft_status()
                if minecraft_result['success']:
                    self.logger.info("Serveur complètement opérationnel")
                    return True

            # Attendre 10 secondes avant la prochaine vérification
            await asyncio.sleep(10)

        self.logger.error(f"Timeout d'attente du démarrage ({timeout}s)")
        return False

    async def wait_for_shutdown(self, timeout: int = 60) -> bool:
        """Attend que le serveur soit arrêté"""
        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Vérifier que Proxmox n'est plus accessible
            proxmox_result = await self.check_proxmox_status()
            if not proxmox_result['success']:
                self.logger.info("Serveur arrêté avec succès")
                return True

            # Attendre 5 secondes avant la prochaine vérification
            await asyncio.sleep(5)

        self.logger.error(f"Timeout d'attente de l'arrêt ({timeout}s)")
        return False
```

## 🔄 **Migration du code existant**

### **1. Supprimer les références PowerShell**

```python
# AVANT (PowerShell)
class PowerShellWrapper:
    async def execute_script(self, script_path: str, args: list = None):
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
        # ... code PowerShell

# APRÈS (Python natif)
class ServerManager:
    async def wake_server(self, mac_address: str, target_host: str):
        return await self.wake_on_lan.wake_server(mac_address, target_host)
```

### **2. Mettre à jour le Dockerfile**

```dockerfile
# AVANT (avec PowerShell)
FROM python:3.11-slim
RUN apt-get update && apt-get install -y powershell

# APRÈS (Python natif uniquement)
FROM python:3.11-slim
# Plus besoin d'installer PowerShell !
```

### **3. Mettre à jour requirements.txt**

```python
# requirements.txt - Version finale
discord.py>=2.6.3
pyyaml>=6.0
python-dotenv>=1.0.0
wakeonlan>=3.0.0          # NOUVEAU
paramiko>=3.4.0           # NOUVEAU
asyncio-subprocess>=0.1.0 # NOUVEAU
psutil>=5.9.0
```

## ✅ **Avantages de la refactorisation**

1. **✅ Cohérence technologique** : Tout en Python
2. **✅ Performance améliorée** : Pas d'overhead PowerShell
3. **✅ Image Docker plus légère** : Moins de dépendances
4. **✅ Maintenance simplifiée** : Un seul langage
5. **✅ Meilleure intégration** : Gestion d'erreur native
6. **✅ Tests plus faciles** : Mocking Python standard

## 🧪 **Tests à implémenter**

```python
import pytest
from unittest.mock import Mock, patch

class TestServerManager:
    """Tests pour le nouveau ServerManager Python natif"""

    @pytest.mark.asyncio
    async def test_wake_server_success(self):
        """Test wake-on-LAN réussi"""
        with patch('wakeonlan.send_magic_packet') as mock_wake:
            mock_wake.return_value = None

            server_manager = ServerManager(config, logger)
            result = await server_manager.wake_server("00:23:7D:FD:C0:5C", "192.168.1.245")

            assert result['success'] == True
            assert result['message'] == "Magic Packet envoyé avec succès"

    @pytest.mark.asyncio
    async def test_shutdown_server_success(self):
        """Test shutdown réussi"""
        with patch('paramiko.SSHClient') as mock_ssh:
            mock_client = Mock()
            mock_ssh.return_value = mock_client
            mock_client.exec_command.return_value = (None, Mock(), Mock())

            server_manager = ServerManager(config, logger)
            result = await server_manager.shutdown_server("192.168.1.245", "root", "./keys/proxmox_key")

            assert result['success'] == True
            assert result['message'] == "Commande d'arrêt envoyée avec succès"
```

## 📋 **Checklist de validation**

- [ ] Tous les scripts PowerShell remplacés par des modules Python
- [ ] Nouvelles dépendances ajoutées à requirements.txt
- [ ] Tests unitaires implémentés
- [ ] Dockerfile mis à jour (suppression PowerShell)
- [ ] Documentation mise à jour
- [ ] Tests d'intégration validés
- [ ] Performance vérifiée
- [ ] Gestion d'erreur testée

## 🚀 **Livrables attendus**

1. **Code source** : Modules Python natifs complets
2. **Tests** : Suite de tests unitaires et d'intégration
3. **Documentation** : README mis à jour
4. **Dockerfile** : Version sans PowerShell
5. **Requirements** : Fichier de dépendances mis à jour

---

**Objectif** : Avoir un bot 100% Python natif, plus performant et plus maintenable ! 🎯
