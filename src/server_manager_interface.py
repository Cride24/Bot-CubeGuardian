"""
Gestionnaire de serveurs pour Bot CubeGuardian - Version Python natif
Gestion des serveurs Proxmox et Minecraft avec modules Python natifs
"""

import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from .server_manager.server_manager import ServerManager as NativeServerManager

@dataclass
class ServerConfig:
    """Configuration d'un serveur"""
    name: str
    ipv4: str
    mac_address: Optional[str] = None
    ssh_user: Optional[str] = None
    ssh_key_path: Optional[str] = None
    web_interface: Optional[str] = None
    port: Optional[int] = None
    timeout: int = 5
    startup_delay: int = 60

class ServerManager:
    """Gestionnaire des serveurs Proxmox et Minecraft - Version Python natif"""
    
    def __init__(self, config_manager, log_manager):
        """
        Initialise le gestionnaire de serveurs
        
        Args:
            config_manager: Gestionnaire de configuration
            log_manager: Gestionnaire de logs
        """
        self.config_manager = config_manager
        self.log_manager = log_manager
        self.logger = logging.getLogger('CubeGuardian.ServerManager')
        
        # Configuration des serveurs
        self.proxmox_config = self._load_server_config('proxmox')
        self.minecraft_config = self._load_server_config('minecraft')
        
        # Configuration pour le module natif
        self.native_config = {
            'proxmox': {
                'name': self.proxmox_config.name,
                'node_name': self.config_manager.get_server_config('proxmox').get('node_name', 'pve'),
                'ipv4': self.proxmox_config.ipv4,
                'mac_address': self.proxmox_config.mac_address,
                'ssh_user': self.proxmox_config.ssh_user,
                'ssh_key_path': self.proxmox_config.ssh_key_path,
                'web_interface': self.proxmox_config.web_interface,
                # Configuration API REST
                'api_url': self.config_manager.get_server_config('proxmox').get('api_url'),
                'api_token_id': self.config_manager.get_server_config('proxmox').get('api_token_id'),
                'api_token_secret': self.config_manager.get_server_config('proxmox').get('api_token_secret')
            },
            'minecraft': {
                'name': self.minecraft_config.name,
                'ipv4': self.minecraft_config.ipv4,
                'port': self.minecraft_config.port,
                'timeout': self.minecraft_config.timeout,
                'startup_delay': self.minecraft_config.startup_delay
            }
        }
        
        # Module natif Python
        self.native_server_manager = NativeServerManager(self.native_config, self.logger)
        
        # État des serveurs
        self.proxmox_status = False
        self.minecraft_status = False
        
        self.logger.info("ServerManager initialisé (Version Python natif)")
    
    def _load_server_config(self, server_name: str) -> ServerConfig:
        """
        Charge la configuration d'un serveur
        
        Args:
            server_name: Nom du serveur (proxmox, minecraft)
            
        Returns:
            Configuration du serveur
        """
        config = self.config_manager.get_server_config(server_name)
        
        return ServerConfig(
            name=config.get('name', server_name.title()),
            ipv4=config.get('ipv4', ''),
            mac_address=config.get('mac_address'),
            ssh_user=config.get('ssh_user'),
            ssh_key_path=config.get('ssh_key_path'),
            web_interface=config.get('web_interface'),
            port=config.get('port'),
            timeout=config.get('timeout', 5),
            startup_delay=config.get('startup_delay', 60)
        )
    
    async def wake_server(self) -> bool:
        """
        Envoie le Magic Packet Wake-on-LAN au serveur Proxmox
        
        Returns:
            True si le wake-on-LAN a réussi
        """
        try:
            self.logger.info(f"Démarrage du serveur Proxmox {self.proxmox_config.name}")
            
            result = await self.native_server_manager.wake_server()
            
            if result['success']:
                self.logger.info("Magic Packet envoyé avec succès")
                self.log_manager.log_server_event('start', 'Proxmox', 'Wake-on-LAN envoyé')
                return True
            else:
                self.logger.error(f"Échec du wake-on-LAN: {result.get('error', 'Erreur inconnue')}")
                self.log_manager.log_server_event('error', 'Proxmox', f"Wake-on-LAN échoué: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors du wake-on-LAN: {e}")
            self.log_manager.log_server_event('error', 'Proxmox', f"Exception: {e}")
            return False
    
    async def shutdown_server(self, delay_seconds: int = 0) -> bool:
        """
        Arrête le nœud Proxmox via API REST
        
        Args:
            delay_seconds: Délai avant arrêt (secondes)
            
        Returns:
            True si l'arrêt a réussi
        """
        try:
            self.logger.info(f"Arrêt du nœud Proxmox {self.proxmox_config.name}")
            
            result = await self.native_server_manager.shutdown_server(delay_seconds)
            
            if result['success']:
                self.logger.info("Commande d'arrêt du nœud envoyée avec succès via API REST")
                self.log_manager.log_server_event('stop', 'Proxmox', 'Nœud arrêté via API REST')
                return True
            else:
                self.logger.error(f"Échec de l'arrêt: {result.get('error', 'Erreur inconnue')}")
                self.log_manager.log_server_event('error', 'Proxmox', f"Arrêt échoué: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt: {e}")
            self.log_manager.log_server_event('error', 'Proxmox', f"Exception: {e}")
            return False
    
    async def check_proxmox_status(self) -> Dict[str, Any]:
        """
        Vérifie la disponibilité du serveur Proxmox
        
        Returns:
            Dict avec success, message, timestamp, details
        """
        try:
            result = await self.native_server_manager.check_proxmox_status()
            
            if result['success']:
                self.proxmox_status = True
                self.logger.debug("Serveur Proxmox accessible")
            else:
                self.proxmox_status = False
                self.logger.debug(f"Serveur Proxmox inaccessible: {result.get('error', 'Erreur inconnue')}")
            
            return result
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification Proxmox: {e}")
            self.proxmox_status = False
            return {
                "success": False,
                "message": "Erreur lors de la vérification Proxmox",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    async def check_minecraft_status(self) -> Dict[str, Any]:
        """
        Vérifie la disponibilité du serveur Minecraft
        
        Returns:
            Dict avec success, message, timestamp, details
        """
        try:
            result = await self.native_server_manager.check_minecraft_status()
            
            if result['success']:
                self.minecraft_status = True
                self.logger.debug("Serveur Minecraft accessible")
            else:
                self.minecraft_status = False
                self.logger.debug(f"Serveur Minecraft inaccessible: {result.get('error', 'Erreur inconnue')}")
            
            return result
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification Minecraft: {e}")
            self.minecraft_status = False
            return {
                "success": False,
                "message": "Erreur lors de la vérification Minecraft",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    async def wait_for_startup(self, timeout: int = 600) -> bool:
        """
        Attend que le serveur soit disponible
        
        Args:
            timeout: Timeout en secondes (défaut: 10 minutes)
            
        Returns:
            True si le serveur est disponible dans les temps
        """
        self.logger.info(f"Attente du démarrage du serveur (timeout: {timeout}s)")
        
        result = await self.native_server_manager.wait_for_startup(timeout)
        
        if result:
            self.logger.info("Serveur complètement opérationnel")
            self.log_manager.log_server_event('start', 'Minecraft', 'Serveur opérationnel')
            return True
        else:
            self.logger.error(f"Timeout atteint: serveur non disponible après {timeout}s")
            self.log_manager.log_server_event('error', 'Proxmox', f'Timeout après {timeout}s')
            return False
    
    async def wait_for_shutdown(self, timeout: int = 60) -> bool:
        """
        Attend que le serveur soit arrêté
        
        Args:
            timeout: Timeout en secondes (défaut: 1 minute)
            
        Returns:
            True si le serveur est arrêté dans les temps
        """
        self.logger.info(f"Attente de l'arrêt du serveur (timeout: {timeout}s)")
        
        result = await self.native_server_manager.wait_for_shutdown(timeout)
        
        if result:
            self.logger.info("Serveur Proxmox arrêté")
            self.log_manager.log_server_event('stop', 'Proxmox', 'Serveur arrêté confirmé')
            return True
        else:
            self.logger.warning(f"Timeout atteint: serveur toujours accessible après {timeout}s")
            self.log_manager.log_server_event('error', 'Proxmox', f'Arrêt non confirmé après {timeout}s')
            return False
    
    def get_server_status(self) -> Dict[str, bool]:
        """
        Récupère l'état actuel des serveurs
        
        Returns:
            Dictionnaire avec l'état des serveurs
        """
        return {
            'proxmox': self.proxmox_status,
            'minecraft': self.minecraft_status
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Récupère les informations des serveurs
        
        Returns:
            Dictionnaire avec les informations des serveurs
        """
        return {
            'proxmox': {
                'name': self.proxmox_config.name,
                'ipv4': self.proxmox_config.ipv4,
                'web_interface': self.proxmox_config.web_interface,
                'status': self.proxmox_status
            },
            'minecraft': {
                'name': self.minecraft_config.name,
                'ipv4': self.minecraft_config.ipv4,
                'port': self.minecraft_config.port,
                'status': self.minecraft_status
            }
        }
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire de serveurs"""
        return f"ServerManager(proxmox={self.proxmox_status}, minecraft={self.minecraft_status})"
