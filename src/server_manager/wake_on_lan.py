"""
Module de gestion Wake-on-LAN natif Python
Remplace le script PowerShell wakeup-pve-bot.ps1
Version amelioree avec plusieurs methodes d'envoi
"""

import asyncio
import socket
import struct
from datetime import datetime
from typing import Dict, Any, List
import logging

try:
    from wakeonlan import send_magic_packet
    WAKEONLAN_AVAILABLE = True
except ImportError:
    WAKEONLAN_AVAILABLE = False


class WakeOnLANManager:
    """Gestionnaire Wake-on-LAN natif Python avec plusieurs methodes"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def _create_magic_packet(self, mac_address: str) -> bytes:
        """
        Cree un Magic Packet pour Wake-on-LAN
        
        Args:
            mac_address: Adresse MAC (format: "00:23:7D:FD:C0:5C")
            
        Returns:
            Magic Packet en bytes
        """
        # Nettoyer l'adresse MAC
        mac_clean = mac_address.replace(':', '').replace('-', '').replace(' ', '')
        
        # Verifier le format
        if len(mac_clean) != 12:
            raise ValueError(f"Adresse MAC invalide: {mac_address}")
        
        # Convertir en bytes
        mac_bytes = bytes.fromhex(mac_clean)
        
        # Creer le Magic Packet: 6 bytes de 0xFF + 16 repetitions de l'adresse MAC
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        return magic_packet

    def _send_magic_packet_raw(self, mac_address: str, broadcast_addresses: List[str] = None) -> bool:
        """
        Envoie un Magic Packet en utilisant socket UDP brut
        
        Args:
            mac_address: Adresse MAC du serveur
            broadcast_addresses: Liste des adresses de broadcast a utiliser
            
        Returns:
            True si au moins un paquet a ete envoye avec succes
        """
        if broadcast_addresses is None:
            # Adresses de broadcast par defaut
            broadcast_addresses = [
                '255.255.255.255',  # Broadcast global
                '192.168.1.255',    # Broadcast local
                '192.168.0.255',    # Broadcast reseau alternatif
            ]
        
        magic_packet = self._create_magic_packet(mac_address)
        success_count = 0
        
        for broadcast_addr in broadcast_addresses:
            try:
                # Creer un socket UDP
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                # Envoyer le Magic Packet sur le port 9 (ou 7)
                for port in [9, 7]:
                    try:
                        sock.sendto(magic_packet, (broadcast_addr, port))
                        success_count += 1
                        self.logger.debug(f"Magic Packet envoye vers {broadcast_addr}:{port}")
                    except Exception as e:
                        self.logger.debug(f"Echec envoi vers {broadcast_addr}:{port}: {e}")
                
                sock.close()
                
            except Exception as e:
                self.logger.warning(f"Erreur envoi vers {broadcast_addr}: {e}")
        
        return success_count > 0

    async def wake_server(self, mac_address: str, target_host: str) -> Dict[str, Any]:
        """
        Envoie un Magic Packet Wake-on-LAN avec plusieurs methodes

        Args:
            mac_address: Adresse MAC du serveur (format: "00:23:7D:FD:C0:5C")
            target_host: Adresse IP du serveur (ex: "192.168.1.245")

        Returns:
            Dict avec success, message, timestamp, details
        """
        methods_used = []
        success_count = 0
        
        try:
            # Methode 1: Module wakeonlan (si disponible)
            if WAKEONLAN_AVAILABLE:
                try:
                    self.logger.debug("Tentative avec module wakeonlan")
                    send_magic_packet(mac_address)
                    methods_used.append("wakeonlan_module")
                    success_count += 1
                    self.logger.debug("Module wakeonlan: succes")
                except Exception as e:
                    self.logger.warning(f"Module wakeonlan echoue: {e}")
                    methods_used.append(f"wakeonlan_module_failed: {e}")
            
            # Methode 2: Socket UDP brut avec broadcast global
            try:
                self.logger.debug("Tentative avec socket UDP brut")
                if self._send_magic_packet_raw(mac_address, ['255.255.255.255']):
                    methods_used.append("socket_udp_global")
                    success_count += 1
                    self.logger.debug("Socket UDP global: succes")
            except Exception as e:
                self.logger.warning(f"Socket UDP global echoue: {e}")
                methods_used.append(f"socket_udp_global_failed: {e}")
            
            # Methode 3: Socket UDP brut avec broadcast local
            try:
                self.logger.debug("Tentative avec socket UDP local")
                if self._send_magic_packet_raw(mac_address, ['192.168.1.255']):
                    methods_used.append("socket_udp_local")
                    success_count += 1
                    self.logger.debug("Socket UDP local: succes")
            except Exception as e:
                self.logger.warning(f"Socket UDP local echoue: {e}")
                methods_used.append(f"socket_udp_local_failed: {e}")
            
            # Methode 4: Socket UDP brut avec adresse IP specifique
            try:
                self.logger.debug("Tentative avec adresse IP specifique")
                if self._send_magic_packet_raw(mac_address, [target_host]):
                    methods_used.append("socket_udp_direct")
                    success_count += 1
                    self.logger.debug("Socket UDP direct: succes")
            except Exception as e:
                self.logger.warning(f"Socket UDP direct echoue: {e}")
                methods_used.append(f"socket_udp_direct_failed: {e}")

            # Determiner le resultat
            if success_count > 0:
                result = {
                    "success": True,
                    "message": f"Magic Packet envoye avec succes ({success_count} methodes)",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "details": {
                        "mac_address": mac_address,
                        "target_host": target_host,
                        "methods_used": methods_used,
                        "success_count": success_count,
                        "operation": "wake_on_lan_enhanced"
                    }
                }
                self.logger.info(f"Wake-on-LAN reussi pour {target_host} ({success_count} methodes)")
            else:
                result = {
                    "success": False,
                    "message": "Toutes les methodes d'envoi ont echoue",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": "Aucune methode n'a reussi",
                    "details": {
                        "mac_address": mac_address,
                        "target_host": target_host,
                        "methods_used": methods_used,
                        "success_count": success_count,
                        "operation": "wake_on_lan_enhanced"
                    }
                }
                self.logger.error(f"Wake-on-LAN echoue pour {target_host} - toutes les methodes ont echoue")

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
                    "methods_used": methods_used,
                    "operation": "wake_on_lan_enhanced"
                }
            }
            self.logger.error(f"Erreur Wake-on-LAN: {e}")
            return result
