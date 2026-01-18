"""
Module de vérification Minecraft natif Python
Remplace le script PowerShell check-minecraft-bot.ps1
"""

import asyncio
import socket
from datetime import datetime
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
