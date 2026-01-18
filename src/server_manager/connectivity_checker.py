"""
Module de vérification de connectivité natif Python
Remplace le script PowerShell check-proxmox-bot.ps1
"""

import asyncio
import socket
import subprocess
from datetime import datetime
from typing import Dict, Any
import logging


class ConnectivityChecker:
    """Vérificateur de connectivité natif Python"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def check_proxmox_connectivity(self, target_host: str, timeout_seconds: int = 10) -> Dict[str, Any]:
        """
        Vérifie la connectivité Proxmox (test TCP sur port 8006)

        Args:
            target_host: Adresse IP du serveur Proxmox
            timeout_seconds: Timeout en secondes

        Returns:
            Dict avec success, message, timestamp, details
        """
        try:
            # Test de connectivité TCP sur le port Proxmox (8006)
            start_time = datetime.now()
            
            # Test de connexion TCP asynchrone
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target_host, 8006),
                    timeout=timeout_seconds
                )
                
                # Fermer la connexion
                writer.close()
                await writer.wait_closed()
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                result = {
                    "success": True,
                    "message": "Serveur Proxmox accessible",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "target_host": target_host,
                        "port": 8006,
                        "response_time": f"{response_time:.2f}s",
                        "operation": "tcp_connectivity_check"
                    }
                }
                self.logger.info(f"Proxmox {target_host}:8006 accessible ({response_time:.2f}s)")
                return result
                
            except asyncio.TimeoutError:
                result = {
                    "success": False,
                    "message": "Serveur Proxmox inaccessible (timeout)",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "target_host": target_host,
                        "port": 8006,
                        "timeout": timeout_seconds,
                        "operation": "tcp_connectivity_check"
                    }
                }
                self.logger.warning(f"Proxmox {target_host}:8006 timeout après {timeout_seconds}s")
                return result
                
            except ConnectionRefusedError:
                result = {
                    "success": False,
                    "message": "Serveur Proxmox inaccessible (connexion refusée)",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "target_host": target_host,
                        "port": 8006,
                        "operation": "tcp_connectivity_check"
                    }
                }
                self.logger.warning(f"Proxmox {target_host}:8006 connexion refusée")
                return result

        except Exception as e:
            result = {
                "success": False,
                "message": "Erreur lors de la vérification de connectivité",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
                "details": {
                    "target_host": target_host,
                    "operation": "tcp_connectivity_check"
                }
            }

            self.logger.error(f"Erreur connectivité Proxmox: {e}")
            return result
