"""
Tests pour les modules de gestion des serveurs Python natifs
Remplace les tests des scripts PowerShell
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import des modules natifs
from src.server_manager.wake_on_lan import WakeOnLANManager
from src.server_manager.ssh_manager import SSHManager
from src.server_manager.connectivity_checker import ConnectivityChecker
from src.server_manager.minecraft_checker import MinecraftChecker
from src.server_manager.server_manager import ServerManager as NativeServerManager


class TestWakeOnLANManager:
    """Tests pour le module Wake-on-LAN natif"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.logger = Mock()
        self.wake_manager = WakeOnLANManager(self.logger)

    @pytest.mark.asyncio
    async def test_wake_server_success(self):
        """Test wake-on-LAN réussi"""
        with patch('wakeonlan.send_magic_packet') as mock_wake:
            mock_wake.return_value = None

            result = await self.wake_manager.wake_server("00:23:7D:FD:C0:5C", "192.168.1.245")

            assert result['success'] == True
            assert result['message'] == "Magic Packet envoyé avec succès"
            assert result['details']['mac_address'] == "00:23:7D:FD:C0:5C"
            assert result['details']['target_host'] == "192.168.1.245"
            assert result['details']['operation'] == "wake_on_lan"

    @pytest.mark.asyncio
    async def test_wake_server_failure(self):
        """Test wake-on-LAN échoué"""
        with patch('wakeonlan.send_magic_packet') as mock_wake:
            mock_wake.side_effect = Exception("Erreur réseau")

            result = await self.wake_manager.wake_server("00:23:7D:FD:C0:5C", "192.168.1.245")

            assert result['success'] == False
            assert result['message'] == "Erreur lors de l'envoi du Magic Packet"
            assert result['error'] == "Erreur réseau"


class TestSSHManager:
    """Tests pour le module SSH natif"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.logger = Mock()
        self.ssh_manager = SSHManager(self.logger)

    @pytest.mark.asyncio
    async def test_shutdown_server_success(self):
        """Test shutdown réussi"""
        with patch('paramiko.SSHClient') as mock_ssh:
            mock_client = Mock()
            mock_ssh.return_value = mock_client
            mock_client.exec_command.return_value = (None, Mock(), Mock())
            mock_client.exec_command.return_value[1].channel.recv_exit_status.return_value = 0

            result = await self.ssh_manager.shutdown_server("192.168.1.245", "root", "./keys/proxmox_key")

            assert result['success'] == True
            assert result['message'] == "Commande d'arrêt envoyée avec succès"
            assert result['details']['target_host'] == "192.168.1.245"
            assert result['details']['operation'] == "shutdown"

    @pytest.mark.asyncio
    async def test_shutdown_server_failure(self):
        """Test shutdown échoué"""
        with patch('paramiko.SSHClient') as mock_ssh:
            mock_ssh.side_effect = Exception("Erreur de connexion SSH")

            result = await self.ssh_manager.shutdown_server("192.168.1.245", "root", "./keys/proxmox_key")

            assert result['success'] == False
            assert result['message'] == "Erreur lors de l'envoi de la commande d'arrêt"
            assert result['error'] == "Erreur de connexion SSH"


class TestConnectivityChecker:
    """Tests pour le module de vérification de connectivité"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.logger = Mock()
        self.connectivity_checker = ConnectivityChecker(self.logger)

    @pytest.mark.asyncio
    async def test_check_proxmox_connectivity_success(self):
        """Test vérification Proxmox réussie"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"ping successful", b"")
            mock_subprocess.return_value = mock_process

            result = await self.connectivity_checker.check_proxmox_connectivity("192.168.1.245")

            assert result['success'] == True
            assert result['message'] == "Serveur Proxmox accessible"
            assert result['details']['target_host'] == "192.168.1.245"
            assert result['details']['operation'] == "connectivity_check"

    @pytest.mark.asyncio
    async def test_check_proxmox_connectivity_failure(self):
        """Test vérification Proxmox échouée"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = (b"", b"ping failed")
            mock_subprocess.return_value = mock_process

            result = await self.connectivity_checker.check_proxmox_connectivity("192.168.1.245")

            assert result['success'] == False
            assert result['message'] == "Serveur Proxmox inaccessible"
            assert result['details']['target_host'] == "192.168.1.245"


class TestMinecraftChecker:
    """Tests pour le module de vérification Minecraft"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.logger = Mock()
        self.minecraft_checker = MinecraftChecker(self.logger)

    @pytest.mark.asyncio
    async def test_check_minecraft_connectivity_success(self):
        """Test vérification Minecraft réussie"""
        with patch('asyncio.open_connection') as mock_connection:
            mock_reader = Mock()
            mock_writer = Mock()
            mock_writer.close.return_value = None
            mock_writer.wait_closed.return_value = None
            mock_connection.return_value = (mock_reader, mock_writer)

            result = await self.minecraft_checker.check_minecraft_connectivity("192.168.1.245", 25565)

            assert result['success'] == True
            assert result['message'] == "Serveur Minecraft accessible"
            assert result['details']['target_host'] == "192.168.1.245"
            assert result['details']['port'] == 25565
            assert result['details']['operation'] == "minecraft_check"

    @pytest.mark.asyncio
    async def test_check_minecraft_connectivity_timeout(self):
        """Test vérification Minecraft timeout"""
        with patch('asyncio.open_connection') as mock_connection:
            mock_connection.side_effect = asyncio.TimeoutError()

            result = await self.minecraft_checker.check_minecraft_connectivity("192.168.1.245", 25565)

            assert result['success'] == False
            assert result['message'] == "Serveur Minecraft inaccessible (timeout)"
            assert result['details']['target_host'] == "192.168.1.245"
            assert result['details']['port'] == 25565


class TestNativeServerManager:
    """Tests pour le gestionnaire de serveurs natif unifié"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.logger = Mock()
        self.config = {
            'proxmox': {
                'name': 'LM150g6',
                'ipv4': '192.168.1.245',
                'mac_address': '00:23:7D:FD:C0:5C',
                'ssh_user': 'root',
                'ssh_key_path': './keys/proxmox_key'
            },
            'minecraft': {
                'name': 'Minecraft Server',
                'ipv4': '192.168.1.245',
                'port': 25565,
                'timeout': 5,
                'startup_delay': 60
            }
        }
        self.server_manager = NativeServerManager(self.config, self.logger)

    @pytest.mark.asyncio
    async def test_wake_server(self):
        """Test wake-on-LAN du serveur"""
        with patch.object(self.server_manager.wake_on_lan, 'wake_server') as mock_wake:
            mock_wake.return_value = {
                'success': True,
                'message': 'Magic Packet envoyé avec succès',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'details': {'operation': 'wake_on_lan'}
            }

            result = await self.server_manager.wake_server()

            assert result['success'] == True
            assert result['message'] == 'Magic Packet envoyé avec succès'

    @pytest.mark.asyncio
    async def test_shutdown_server(self):
        """Test arrêt du serveur"""
        with patch.object(self.server_manager.ssh_manager, 'shutdown_server') as mock_shutdown:
            mock_shutdown.return_value = {
                'success': True,
                'message': 'Commande d\'arrêt envoyée avec succès',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'details': {'operation': 'shutdown'}
            }

            result = await self.server_manager.shutdown_server()

            assert result['success'] == True
            assert result['message'] == 'Commande d\'arrêt envoyée avec succès'

    @pytest.mark.asyncio
    async def test_check_proxmox_status(self):
        """Test vérification du statut Proxmox"""
        with patch.object(self.server_manager.connectivity_checker, 'check_proxmox_connectivity') as mock_check:
            mock_check.return_value = {
                'success': True,
                'message': 'Serveur Proxmox accessible',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'details': {'operation': 'connectivity_check'}
            }

            result = await self.server_manager.check_proxmox_status()

            assert result['success'] == True
            assert result['message'] == 'Serveur Proxmox accessible'

    @pytest.mark.asyncio
    async def test_check_minecraft_status(self):
        """Test vérification du statut Minecraft"""
        with patch.object(self.server_manager.minecraft_checker, 'check_minecraft_connectivity') as mock_check:
            mock_check.return_value = {
                'success': True,
                'message': 'Serveur Minecraft accessible',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'details': {'operation': 'minecraft_check'}
            }

            result = await self.server_manager.check_minecraft_status()

            assert result['success'] == True
            assert result['message'] == 'Serveur Minecraft accessible'

    @pytest.mark.asyncio
    async def test_wait_for_startup_success(self):
        """Test attente du démarrage réussi"""
        with patch.object(self.server_manager, 'check_proxmox_status') as mock_proxmox, \
             patch.object(self.server_manager, 'check_minecraft_status') as mock_minecraft:
            
            mock_proxmox.return_value = True
            mock_minecraft.return_value = True

            result = await self.server_manager.wait_for_startup(timeout=10)

            assert result == True

    @pytest.mark.asyncio
    async def test_wait_for_startup_timeout(self):
        """Test attente du démarrage timeout"""
        with patch.object(self.server_manager, 'check_proxmox_status') as mock_proxmox:
            mock_proxmox.return_value = False

            result = await self.server_manager.wait_for_startup(timeout=1)

            assert result == False

    @pytest.mark.asyncio
    async def test_wait_for_shutdown_success(self):
        """Test attente de l'arrêt réussi"""
        with patch.object(self.server_manager, 'check_proxmox_status') as mock_proxmox:
            mock_proxmox.return_value = False

            result = await self.server_manager.wait_for_shutdown(timeout=10)

            assert result == True

    @pytest.mark.asyncio
    async def test_wait_for_shutdown_timeout(self):
        """Test attente de l'arrêt timeout"""
        with patch.object(self.server_manager, 'check_proxmox_status') as mock_proxmox:
            mock_proxmox.return_value = True

            result = await self.server_manager.wait_for_shutdown(timeout=1)

            assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
