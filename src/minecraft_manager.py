#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Manager - Gestion spécifique du serveur Minecraft
Redémarrages LXC Proxmox, cooldowns, monitoring
"""

import asyncio
import logging
import aiohttp
import time
from typing import Dict, Optional, Any
from datetime import datetime

class MinecraftManager:
    """
    Gestionnaire spécifique du serveur Minecraft
    Intègre le SecurityManager pour cooldowns et LXC Proxmox pour redémarrages
    """
    
    def __init__(self, config_manager, server_manager, security_manager, log_manager):
        """
        Initialise le gestionnaire Minecraft
        
        Args:
            config_manager: Gestionnaire de configuration
            server_manager: Gestionnaire de serveurs Proxmox
            security_manager: Gestionnaire de sécurité
            log_manager: Gestionnaire de logs
        """
        self.config_manager = config_manager
        self.server_manager = server_manager
        self.security_manager = security_manager
        self.log_manager = log_manager
        self.logger = logging.getLogger('CubeGuardian.MinecraftManager')
        
        # Configuration Minecraft
        self.container_id = 105  # LXC-game selon le cahier des charges
        self.restart_timeout = 300  # 5 minutes max pour redémarrage
        self.monitoring_interval = 10  # Vérification toutes les 10 secondes
        
        # Protection anti-spam pour redémarrages
        self.restart_in_progress = False  # Verrou global de redémarrage
        self.pending_confirmations = {}  # {user_id: timestamp} pour confirmations en attente
        
        # Configuration Proxmox (depuis config_manager) - MAPPING CORRIGÉ
        self.proxmox_config = {
            'host': self.config_manager.get_server_config('proxmox').get('ipv4', '192.168.1.245'),
            'port': 8006,  # Extrait de l'API URL ou défaut
            'node': self.config_manager.get_server_config('proxmox').get('node_name', 'pve'),
            'api_token_id': self.config_manager.get_server_config('proxmox').get('api_token_id'),
            'api_token_secret': self.config_manager.get_server_config('proxmox').get('api_token_secret'),
            'verify_ssl': False  # SSL non vérifié pour serveur local
        }
        
        self.logger.info("MinecraftManager initialisé")

    # ========================================
    # 🛡️ MÉTHODES DE SÉCURITÉ (délégation au SecurityManager)
    # ========================================

    def check_user_cooldown(self, user_id: int) -> bool:
        """
        Vérifie si l'utilisateur peut exécuter une commande (cooldown 10min)
        Délègue au SecurityManager
        
        Args:
            user_id: ID de l'utilisateur Discord
            
        Returns:
            True si l'utilisateur peut exécuter une commande, False sinon
        """
        return self.security_manager.check_user_cooldown(user_id)

    def update_user_cooldown(self, user_id: int) -> None:
        """
        Met à jour le cooldown de l'utilisateur après une commande réussie
        Délègue au SecurityManager
        
        Args:
            user_id: ID de l'utilisateur Discord
        """
        self.security_manager.update_user_cooldown(user_id)

    def get_user_cooldown_remaining(self, user_id: int) -> int:
        """
        Récupère le temps restant du cooldown en minutes
        Délègue au SecurityManager
        
        Args:
            user_id: ID de l'utilisateur Discord
            
        Returns:
            Nombre de minutes restantes (0 si pas de cooldown)
        """
        return self.security_manager.get_user_cooldown_remaining(user_id)

    # ========================================
    # 🎮 MÉTHODES MINECRAFT SPÉCIFIQUES
    # ========================================

    async def restart_minecraft_server(self, user: Any, channel: Any) -> Dict[str, Any]:
        """
        Redémarre le conteneur Minecraft via API Proxmox LXC
        
        Args:
            user: Utilisateur Discord qui demande le redémarrage
            channel: Canal Discord pour feedback
            
        Returns:
            Dictionnaire avec le résultat du redémarrage
        """
        try:
            user_id = user.id
            start_time = time.time()
            
            self.logger.info(f"Début redémarrage Minecraft pour utilisateur {user.name} (ID: {user_id})")
            
            # 1. Vérification finale de sécurité
            spam_detected, spam_reason = self.security_manager.check_spam_detection(user_id)
            if spam_detected:
                self.logger.warning(f"Tentative de spam détectée: {spam_reason}")
                return {
                    'success': False,
                    'error': 'spam_detected',
                    'details': spam_reason
                }
            
            # 1.1 MARQUER le redémarrage comme en cours (la vérification est faite dans bot.py)
            self.restart_in_progress = True
            
            # 2. Exécution du redémarrage LXC
            restart_result = await self._execute_lxc_restart()
            
            if not restart_result['success']:
                return restart_result
            
            # 3. Surveillance du redémarrage
            monitoring_result = await self._monitor_restart_completion(start_time)
            
            if monitoring_result['success']:
                # 4. Mise à jour du cooldown en cas de succès
                self.update_user_cooldown(user_id)
                
                elapsed_time = int(time.time() - start_time)
                
                self.logger.info(f"Redémarrage Minecraft réussi en {elapsed_time}s pour {user.name}")
                
                return {
                    'success': True,
                    'elapsed_time': elapsed_time,
                    'container_id': self.container_id,
                    'user_id': user_id
                }
            else:
                return monitoring_result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du redémarrage Minecraft: {e}")
            return {
                'success': False,
                'error': 'unexpected_error',
                'details': str(e)
            }
        finally:
            # NETTOYER les verrous dans tous les cas (succès, échec, exception)
            self.restart_in_progress = False
            if user_id in self.pending_confirmations:
                del self.pending_confirmations[user_id]
            self.logger.debug(f"Verrous de redémarrage nettoyés pour {user.name}")

    async def _execute_lxc_restart(self) -> Dict[str, Any]:
        """
        Exécute le redémarrage LXC GRACIEUX via API Proxmox (shutdown + start)
        
        Étapes:
        1. Arrêt gracieux du conteneur (save-all automatique)
        2. Attente arrêt complet 
        3. Redémarrage du conteneur
        
        Returns:
            Résultat de l'opération de redémarrage
        """
        try:
            self.logger.info(f"Redémarrage GRACIEUX conteneur LXC {self.container_id} via API Proxmox")
            
            # Configuration API
            base_url = f"https://{self.proxmox_config['host']}:{self.proxmox_config['port']}"
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f"PVEAPIToken={self.proxmox_config['api_token_id']}={self.proxmox_config['api_token_secret']}"
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(verify_ssl=self.proxmox_config['verify_ssl'])
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                
                # 1. ARRÊT GRACIEUX du conteneur
                shutdown_url = f"{base_url}/api2/json/nodes/{self.proxmox_config['node']}/lxc/{self.container_id}/status/shutdown"
                
                self.logger.info(f"Étape 1/3: Arrêt gracieux LXC {self.container_id}")
                async with session.post(shutdown_url, headers=headers) as shutdown_response:
                    if shutdown_response.status != 200:
                        error_text = await shutdown_response.text()
                        return {
                            'success': False,
                            'error': 'shutdown_failed',
                            'details': f"Arrêt gracieux échoué - Status {shutdown_response.status}: {error_text}"
                        }
                
                # 2. ATTENDRE que le conteneur soit complètement arrêté
                self.logger.info(f"Étape 2/3: Attente arrêt complet LXC {self.container_id}")
                max_wait = 120  # 120 secondes max pour arrêt gracieux
                wait_interval = 2
                
                for attempt in range(max_wait // wait_interval):
                    status_result = await self._check_lxc_status()
                    if status_result['success'] and status_result['status'] == 'stopped':
                        self.logger.info(f"LXC {self.container_id} arrêté avec succès après {attempt * wait_interval}s")
                        break
                    
                    await asyncio.sleep(wait_interval)
                else:
                    return {
                        'success': False,
                        'error': 'shutdown_timeout',
                        'details': f"Timeout: LXC pas arrêté après {max_wait}s"
                    }
                
                # 3. REDÉMARRAGE du conteneur
                start_url = f"{base_url}/api2/json/nodes/{self.proxmox_config['node']}/lxc/{self.container_id}/status/start"
                
                self.logger.info(f"Étape 3/3: Redémarrage LXC {self.container_id}")
                async with session.post(start_url, headers=headers) as start_response:
                    if start_response.status == 200:
                        self.logger.info(f"Redémarrage gracieux LXC {self.container_id} initié avec succès")
                        return {
                            'success': True,
                            'container_id': self.container_id,
                            'operation': 'graceful_restart',
                            'timestamp': time.time()
                        }
                    else:
                        error_text = await start_response.text()
                        return {
                            'success': False,
                            'error': 'start_failed',
                            'details': f"Redémarrage échoué - Status {start_response.status}: {error_text}"
                        }
            
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'timeout',
                'details': "Timeout lors de la communication avec Proxmox"
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'api_error',
                'details': f"Erreur API Proxmox: {str(e)}"
            }

    async def _monitor_restart_completion(self, start_time: float) -> Dict[str, Any]:
        """
        Surveille la completion du redémarrage
        
        Args:
            start_time: Timestamp du début du redémarrage
            
        Returns:
            Résultat de la surveillance
        """
        try:
            self.logger.info(f"Surveillance du redémarrage LXC {self.container_id}")
            
            # Attendre le délai de démarrage Minecraft (comme au boot initial)
            startup_delay = self.config_manager.get_server_config('minecraft').get('startup_delay', 60)
            self.logger.info(f"Attente startup_delay de {startup_delay}s pour démarrage Minecraft")
            await asyncio.sleep(startup_delay)
            
            max_attempts = self.restart_timeout // self.monitoring_interval
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                elapsed = int(time.time() - start_time)
                
                self.logger.debug(f"Surveillance tentative {attempt}/{max_attempts} - {elapsed}s écoulées")
                
                # Vérifier le statut du conteneur
                status_result = await self._check_lxc_status()
                
                if status_result['success']:
                    if status_result['status'] == 'running':
                        # Vérification ROBUSTE: utiliser la même méthode que le démarrage initial
                        minecraft_status = await self.server_manager.check_minecraft_status()
                        
                        if minecraft_status['success']:
                            self.logger.info(f"Redémarrage LXC {self.container_id} terminé avec succès en {elapsed}s")
                            self.logger.info(f"Minecraft Server VRAIMENT disponible sur {minecraft_status.get('details', {}).get('target_host')}:{minecraft_status.get('details', {}).get('port')}")
                            return {
                                'success': True,
                                'elapsed_time': elapsed,
                                'attempts': attempt
                            }
                        else:
                            self.logger.debug(f"LXC running mais Minecraft pas encore accessible - {minecraft_status.get('message', 'Erreur inconnue')}")
                    else:
                        self.logger.debug(f"LXC status: {status_result['status']}")
                else:
                    self.logger.warning(f"Erreur lors de la vérification du statut: {status_result}")
                
                # Attendre avant la prochaine vérification
                await asyncio.sleep(self.monitoring_interval)
            
            # Timeout atteint
            elapsed = int(time.time() - start_time)
            self.logger.error(f"Timeout du redémarrage après {elapsed}s ({max_attempts} tentatives)")
            
            return {
                'success': False,
                'error': 'restart_timeout',
                'details': f"Redémarrage non terminé après {elapsed}s",
                'elapsed_time': elapsed,
                'attempts': attempt
            }
            
        except Exception as e:
            elapsed = int(time.time() - start_time)
            self.logger.error(f"Erreur lors de la surveillance: {e}")
            return {
                'success': False,
                'error': 'monitoring_error',
                'details': str(e),
                'elapsed_time': elapsed
            }

    async def _check_lxc_status(self) -> Dict[str, Any]:
        """
        Vérifie le statut du conteneur LXC
        
        Returns:
            Statut du conteneur
        """
        try:
            # Utiliser le server_manager existant si possible
            if hasattr(self.server_manager, 'check_proxmox_status'):
                proxmox_result = await self.server_manager.check_proxmox_status()
                if not proxmox_result.get('success', False):
                    return {
                        'success': False,
                        'error': 'proxmox_unreachable',
                        'details': 'Serveur Proxmox non accessible'
                    }
            
            # API call direct pour le statut LXC
            base_url = f"https://{self.proxmox_config['host']}:{self.proxmox_config['port']}"
            status_url = f"{base_url}/api2/json/nodes/{self.proxmox_config['node']}/lxc/{self.container_id}/status/current"
            
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector(verify_ssl=self.proxmox_config['verify_ssl'])
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                # Headers avec authentification API Token
                headers = {
                    'Authorization': f"PVEAPIToken={self.proxmox_config['api_token_id']}={self.proxmox_config['api_token_secret']}"
                }
                
                async with session.get(status_url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        status = result.get('data', {}).get('status', 'unknown')
                        return {
                            'success': True,
                            'status': status,
                            'container_id': self.container_id
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'status_check_failed',
                            'details': f"HTTP {response.status}"
                        }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'status_check_error',
                'details': str(e)
            }

    # Méthode _check_minecraft_connectivity() supprimée - remplacée par server_manager.check_minecraft_status() 
    # qui utilise la même vérification robuste que lors du démarrage initial

    def get_minecraft_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du gestionnaire Minecraft
        
        Returns:
            Statistiques diverses
        """
        try:
            security_stats = self.security_manager.get_security_statistics()
            
            return {
                'container_id': self.container_id,
                'restart_timeout': self.restart_timeout,
                'monitoring_interval': self.monitoring_interval,
                'proxmox_host': self.proxmox_config['host'],
                'security_statistics': security_stats,
                'manager_status': 'operational'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {'error': str(e)}
