"""
Module principal de gestion des serveurs - Version Python natif
Unifie tous les sous-modules pour remplacer les scripts PowerShell
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

from .wake_on_lan import WakeOnLANManager
from .ssh_manager import SSHManager
from .proxmox_api import ProxmoxAPI
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
        self.proxmox_api = ProxmoxAPI(logger)
        self.connectivity_checker = ConnectivityChecker(logger)
        self.minecraft_checker = MinecraftChecker(logger)

    async def wake_server(self, mac_address: str = None, target_host: str = None) -> Dict[str, Any]:
        """Wake-on-LAN du serveur Proxmox"""
        mac_address = mac_address or self.config['proxmox']['mac_address']
        target_host = target_host or self.config['proxmox']['ipv4']

        return await self.wake_on_lan.wake_server(mac_address, target_host)

    async def shutdown_server(self, delay_seconds: int = 0) -> Dict[str, Any]:
        """Arrêt simple du nœud Proxmox via API REST (Proxmox gère automatiquement l'arrêt des conteneurs)"""
        try:
            api_url = self.config['proxmox']['api_url']
            token_id = self.config['proxmox']['api_token_id']
            token_secret = self.config['proxmox']['api_token_secret']
            node_name = self.config['proxmox']['node_name']

            self.logger.info(f"Arrêt simple du nœud Proxmox {node_name}")
            
            async with self.proxmox_api as api:
                # Arrêt direct du nœud (Proxmox gère automatiquement l'arrêt des conteneurs)
                return await api.shutdown_node(api_url, token_id, token_secret, node_name, delay_seconds)
                
        except KeyError as e:
            self.logger.error(f"Configuration manquante: {e}")
            return {
                "success": False,
                "error": f"Configuration manquante: {e}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    async def check_proxmox_status(self, target_host: str = None) -> Dict[str, Any]:
        """Vérification de la connectivité Proxmox via ping (simple et fiable)"""
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
