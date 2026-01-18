"""
Module de gestion SSH natif Python
Remplace le script PowerShell shutdown-pve-bot.ps1
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

try:
    import paramiko
except ImportError:
    # Fallback si paramiko n'est pas installé
    paramiko = None


class SSHManager:
    """Gestionnaire SSH natif Python"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        if paramiko is None:
            raise ImportError("Module paramiko non installé. Installez avec: pip install paramiko")

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
