"""
API Proxmox simplifiée pour l'arrêt du nœud
Version simplifiée qui utilise uniquement l'arrêt du nœud
"""

import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

class ProxmoxAPISimple:
    """API Proxmox simplifiée pour l'arrêt du nœud"""
    
    def __init__(self):
        self.logger = logging.getLogger('CubeGuardian.ProxmoxAPISimple')
    
    async def shutdown_node_simple(self, api_url: str, token_id: str, token_secret: str, node_name: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Arrêt simple du nœud Proxmox via API REST
        
        Args:
            api_url: URL de l'API Proxmox
            token_id: ID du token API
            token_secret: Secret du token API
            node_name: Nom du nœud à arrêter
            timeout: Timeout pour l'arrêt (secondes)
            
        Returns:
            Dictionnaire avec le résultat de l'opération
        """
        try:
            self.logger.info(f"Arrêt simple du nœud {node_name} (timeout: {timeout}s)")
            
            url = f"{api_url}/nodes/{node_name}/status"
            headers = {
                "Authorization": f"PVEAPIToken={token_id}={token_secret}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Données pour l'arrêt propre (sans timeout - non supporté par l'API)
            data = {
                "command": "shutdown"
            }
            
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result_data = await response.json()
                        self.logger.info(f"Nœud {node_name} arrêté avec succès")
                        return {
                            "success": True,
                            "message": f"Nœud {node_name} arrêté",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "details": {
                                "node_name": node_name,
                                "timeout": timeout,
                                "response": result_data
                            }
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Échec de l'arrêt du nœud {node_name}: HTTP {response.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "details": {
                                "node_name": node_name,
                                "timeout": timeout,
                                "status_code": response.status,
                                "response": error_text
                            }
                        }
                        
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt du nœud {node_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "details": {
                    "node_name": node_name,
                    "timeout": timeout,
                    "exception": str(e)
                }
            }
    
    async def check_node_status(self, api_url: str, token_id: str, token_secret: str, node_name: str) -> Dict[str, Any]:
        """
        Vérifie le statut du nœud Proxmox
        
        Args:
            api_url: URL de l'API Proxmox
            token_id: ID du token API
            token_secret: Secret du token API
            node_name: Nom du nœud à vérifier
            
        Returns:
            Dictionnaire avec le statut du nœud
        """
        try:
            url = f"{api_url}/nodes/{node_name}/status"
            headers = {
                "Authorization": f"PVEAPIToken={token_id}={token_secret}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data['data'],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
