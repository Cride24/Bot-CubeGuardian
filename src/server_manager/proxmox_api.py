"""
Module API REST Proxmox natif Python
Remplace le module SSH pour la gestion des VMs via l'API REST
"""

import asyncio
import aiohttp
import ssl
from datetime import datetime
from typing import Dict, Any, Optional
import logging


class ProxmoxAPI:
    """Client API REST Proxmox natif Python"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.session = None

    async def __aenter__(self):
        """Contexte manager pour la session HTTP"""
        # Configuration SSL pour ignorer les certificats auto-signés
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermeture de la session HTTP"""
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, url: str, headers: Dict[str, str] = None, 
                          data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API Proxmox
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            url: URL de la requête
            headers: En-têtes HTTP
            data: Données à envoyer
            
        Returns:
            Réponse de l'API
        """
        try:
            # Utiliser form data si Content-Type est application/x-www-form-urlencoded
            if headers and headers.get("Content-Type") == "application/x-www-form-urlencoded":
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": result.get("data", result),
                            "status": response.status
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status": response.status
                        }
            else:
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": result.get("data", result),
                            "status": response.status
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "status": response.status
                        }
                    
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Timeout de la requête API",
                "status": 408
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur de connexion: {str(e)}",
                "status": 0
            }

    async def get_vm_status(self, api_url: str, token_id: str, token_secret: str, 
                          vm_id: str, node_name: str = "pve") -> Dict[str, Any]:
        """
        Récupère le statut d'une VM
        
        Args:
            api_url: URL de l'API Proxmox
            token_id: ID du token API
            token_secret: Secret du token API
            vm_id: ID de la VM
            node_name: Nom du nœud Proxmox
            
        Returns:
            Statut de la VM
        """
        url = f"{api_url}/nodes/{node_name}/qemu/{vm_id}/status/current"
        headers = {
            "Authorization": f"PVEAPIToken={token_id}={token_secret}"
        }
        
        result = await self._make_request("GET", url, headers)
        
        if result["success"]:
            vm_data = result["data"]
            return {
                "success": True,
                "vm_id": vm_id,
                "status": vm_data.get("status", "unknown"),
                "name": vm_data.get("name", "Unknown"),
                "uptime": vm_data.get("uptime", 0),
                "cpu": vm_data.get("cpu", 0),
                "mem": vm_data.get("mem", 0),
                "maxmem": vm_data.get("maxmem", 0)
            }
        else:
            return result

    async def start_vm(self, api_url: str, token_id: str, token_secret: str, 
                      vm_id: str, node_name: str = "pve") -> Dict[str, Any]:
        """
        Démarre une VM
        
        Args:
            api_url: URL de l'API Proxmox
            token_id: ID du token API
            token_secret: Secret du token API
            vm_id: ID de la VM
            node_name: Nom du nœud Proxmox
            
        Returns:
            Résultat du démarrage
        """
        url = f"{api_url}/nodes/{node_name}/qemu/{vm_id}/status/start"
        headers = {
            "Authorization": f"PVEAPIToken={token_id}={token_secret}"
        }
        
        result = await self._make_request("POST", url, headers)
        
        if result["success"]:
            self.logger.info(f"VM {vm_id} démarrée avec succès")
            return {
                "success": True,
                "message": f"VM {vm_id} démarrée",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            self.logger.error(f"Échec du démarrage de la VM {vm_id}: {result.get('error')}")
            return result

    # Méthode shutdown_containers_first supprimée - Proxmox gère automatiquement l'arrêt des conteneurs

    async def shutdown_node(self, api_url: str, token_id: str, token_secret: str, 
                           node_name: str = "pve", delay: int = 0) -> Dict[str, Any]:
        """
        Arrête le nœud Proxmox
        
        Args:
            api_url: URL de l'API Proxmox
            token_id: ID du token API
            token_secret: Secret du token API
            node_name: Nom du nœud Proxmox
            delay: Délai avant arrêt (secondes)
            
        Returns:
            Résultat de l'arrêt
        """
        url = f"{api_url}/nodes/{node_name}/status"
        headers = {
            "Authorization": f"PVEAPIToken={token_id}={token_secret}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Données pour l'arrêt propre (sans timeout - non supporté par l'API)
        data = {"command": "shutdown"}
        
        result = await self._make_request("POST", url, headers, data)
        
        if result["success"]:
            self.logger.info(f"Nœud {node_name} arrêté avec succès")
            return {
                "success": True,
                "message": f"Nœud {node_name} arrêté",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            self.logger.error(f"Échec de l'arrêt du nœud {node_name}: {result.get('error')}")
            return result

    async def list_vms(self, api_url: str, token_id: str, token_secret: str) -> Dict[str, Any]:
        """
        Liste toutes les VMs
        
        Args:
            api_url: URL de l'API Proxmox
            token_id: ID du token API
            token_secret: Secret du token API
            
        Returns:
            Liste des VMs
        """
        url = f"{api_url}/nodes/pve/qemu"
        headers = {
            "Authorization": f"PVEAPIToken={token_id}={token_secret}"
        }
        
        result = await self._make_request("GET", url, headers)
        
        if result["success"]:
            vms = result["data"]
            return {
                "success": True,
                "vms": vms,
                "count": len(vms)
            }
        else:
            return result

    async def get_node_status(self, api_url: str, token_id: str, token_secret: str, node_name: str = "pve") -> Dict[str, Any]:
        """
        Récupère le statut du nœud Proxmox
        
        Args:
            api_url: URL de l'API Proxmox
            token_id: ID du token API
            token_secret: Secret du token API
            node_name: Nom du nœud Proxmox
            
        Returns:
            Statut du nœud
        """
        url = f"{api_url}/nodes/{node_name}/status"
        headers = {
            "Authorization": f"PVEAPIToken={token_id}={token_secret}"
        }
        
        result = await self._make_request("GET", url, headers)
        
        if result["success"]:
            node_data = result["data"]
            return {
                "success": True,
                "node": node_name,
                "status": "online",
                "uptime": node_data.get("uptime", 0),
                "cpu": node_data.get("cpu", 0),
                "mem": node_data.get("mem", 0),
                "maxmem": node_data.get("maxmem", 0)
            }
        else:
            return result
