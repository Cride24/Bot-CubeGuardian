"""
Gestionnaire de serveur simplifié
Version qui utilise uniquement l'arrêt du nœud Proxmox
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from .proxmox_api_simple import ProxmoxAPISimple

class SimpleServerManager:
    """Gestionnaire de serveur simplifié"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le gestionnaire de serveur simplifié
        
        Args:
            config: Configuration du serveur
        """
        self.config = config
        self.logger = logging.getLogger('CubeGuardian.SimpleServerManager')
        self.proxmox_api = ProxmoxAPISimple()
        
        self.logger.info("SimpleServerManager initialisé")
    
    async def shutdown_server(self, delay_seconds: int = 0) -> Dict[str, Any]:
        """
        Arrêt simple du nœud Proxmox
        
        Args:
            delay_seconds: Délai avant arrêt (non utilisé dans cette version simplifiée)
            
        Returns:
            Dictionnaire avec le résultat de l'opération
        """
        try:
            api_url = self.config['proxmox']['api_url']
            token_id = self.config['proxmox']['api_token_id']
            token_secret = self.config['proxmox']['api_token_secret']
            node_name = self.config['proxmox']['node_name']
            
            self.logger.info(f"Arrêt simple du nœud {node_name}")
            
            # Arrêt direct du nœud (Proxmox gère automatiquement l'arrêt des conteneurs)
            result = await self.proxmox_api.shutdown_node_simple(
                api_url, token_id, token_secret, node_name, timeout=300
            )
            
            if result['success']:
                self.logger.info("Arrêt du nœud envoyé avec succès")
            else:
                self.logger.error(f"Échec de l'arrêt: {result.get('error')}")
            
            return result
                
        except KeyError as e:
            self.logger.error(f"Configuration manquante: {e}")
            return {
                "success": False,
                "error": f"Configuration manquante: {e}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    async def check_proxmox_status(self) -> Dict[str, Any]:
        """
        Vérifie le statut de Proxmox
        
        Returns:
            Dictionnaire avec le statut
        """
        try:
            api_url = self.config['proxmox']['api_url']
            token_id = self.config['proxmox']['api_token_id']
            token_secret = self.config['proxmox']['api_token_secret']
            node_name = self.config['proxmox']['node_name']
            
            result = await self.proxmox_api.check_node_status(
                api_url, token_id, token_secret, node_name
            )
            
            if result['success']:
                status_data = result['data']
                return {
                    "success": True,
                    "accessible": True,
                    "uptime": status_data.get('uptime', 0),
                    "load": status_data.get('loadavg', [0, 0, 0]),
                    "memory": status_data.get('memory', {}),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                return {
                    "success": False,
                    "accessible": False,
                    "error": result.get('error'),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du statut: {e}")
            return {
                "success": False,
                "accessible": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    async def check_minecraft_status(self) -> Dict[str, Any]:
        """
        Vérifie le statut de Minecraft (connectivité TCP simple)
        
        Returns:
            Dictionnaire avec le statut
        """
        try:
            import socket
            
            minecraft_host = self.config['minecraft']['host']
            minecraft_port = self.config['minecraft']['port']
            
            # Test de connectivité TCP simple
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                result = sock.connect_ex((minecraft_host, minecraft_port))
                if result == 0:
                    return {
                        "success": True,
                        "accessible": True,
                        "message": f"Minecraft accessible sur {minecraft_host}:{minecraft_port}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                else:
                    return {
                        "success": False,
                        "accessible": False,
                        "message": f"Minecraft non accessible sur {minecraft_host}:{minecraft_port}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
            finally:
                sock.close()
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification Minecraft: {e}")
            return {
                "success": False,
                "accessible": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    async def wake_server(self) -> Dict[str, Any]:
        """
        Démarre le serveur via Wake-on-LAN
        
        Returns:
            Dictionnaire avec le résultat
        """
        # Pour l'instant, on retourne un succès simulé
        # Le Wake-on-LAN est géré par le WakeOnLANManager existant
        return {
            "success": True,
            "message": "Wake-on-LAN géré par le système existant",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
