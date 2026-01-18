"""
Bot Discord CubeGuardian - Module principal
Bot automatisé pour la gestion du serveur Proxmox/Minecraft basée sur l'activité vocale Discord
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Optional
from enum import Enum

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Import des modules locaux
from .config_manager import ConfigManager
from .log_manager import LogManager
from .server_manager_interface import ServerManager
from .user_manager import UserManager
from .message_manager import MessageManager
from .voice_monitor import VoiceMonitor
from .command_parser import CommandParser, CommandResult, CommandIntent
from .security_manager import SecurityManager
from .minecraft_manager import MinecraftManager

class BotState(Enum):
    """États du bot"""
    IDLE = "idle"                    # En attente
    STARTUP_REQUESTED = "startup"    # Démarrage demandé
    STARTUP_MONITORING = "monitoring" # Surveillance démarrage
    SERVER_OPERATIONAL = "operational" # Serveur opérationnel
    SHUTDOWN_TIMER = "shutdown_timer" # Timer d'arrêt actif
    SHUTDOWN_IN_PROGRESS = "shutdown" # Arrêt en cours
    ERROR = "error"                  # État d'erreur
    MAINTENANCE = "maintenance"      # Mode maintenance

class CubeGuardianBot(commands.Bot):
    """Bot Discord CubeGuardian principal"""
    
    def __init__(self, config_path: str = "./config"):
        """
        Initialise le bot CubeGuardian
        
        Args:
            config_path: Chemin vers le répertoire de configuration
        """
        # Charger les variables d'environnement
        load_dotenv()
        
        # Initialisation des gestionnaires
        self.config_manager = ConfigManager(config_path)
        self.log_manager = LogManager(self.config_manager)
        self.logger = logging.getLogger('CubeGuardian.Bot')
        
        # Configuration Discord
        discord_config = self.config_manager.get_config('discord', {})
        intents = self._get_discord_intents()
        
        # Initialisation du bot Discord
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Gestionnaires
        self.server_manager = ServerManager(self.config_manager, self.log_manager)
        self.user_manager = UserManager(self.config_manager, self.log_manager)
        self.message_manager = MessageManager(self.config_manager, self.log_manager)
        self.command_parser = CommandParser()  # Analyseur de commandes NLP
        self.security_manager = SecurityManager(self.config_manager, self.log_manager)  # Nouveau : Sécurité avancée
        self.minecraft_manager = MinecraftManager(
            self.config_manager, self.server_manager, 
            self.security_manager, self.log_manager
        )  # Nouveau : Gestion Minecraft avec sécurité
        self.voice_monitor = VoiceMonitor(
            self, self.config_manager, self.user_manager, 
            self.message_manager, self.log_manager
        )
        
        # Configurer le nettoyage automatique des données de sécurité
        asyncio.create_task(self._security_cleanup_task())
        
        # État du bot
        self.state = BotState.IDLE
        self.start_time = None
        
        # Configuration des callbacks
        self._setup_voice_monitor_callbacks()
        
        self.logger.info("CubeGuardianBot initialisé")
    
    def _get_discord_intents(self) -> discord.Intents:
        """
        Configure les intents Discord nécessaires
        
        Returns:
            Intents Discord configurés
        """
        intents = discord.Intents.default()
        
        # Intents requis pour la surveillance vocale
        intents.voice_states = True    # Surveillance des salons vocaux
        intents.members = True         # Gestion des membres
        intents.guilds = True          # Accès aux serveurs
        intents.messages = True        # Envoi de messages
        intents.message_content = True # Lecture du contenu des messages
        
        return intents
    
    def _setup_voice_monitor_callbacks(self) -> None:
        """Configure les callbacks du surveillant vocal"""
        self.voice_monitor.set_callbacks(
            on_user_join=self._on_authorized_user_join,
            on_user_leave=self._on_authorized_user_leave,
            on_timer_cancelled=self._on_shutdown_timer_cancelled
        )
    
    async def start(self) -> None:
        """Démarre le bot et la surveillance"""
        try:
            # Validation de la configuration
            if not self.config_manager.validate_config():
                self.logger.error("Configuration invalide, arrêt du bot")
                return
            
            self.logger.info("Démarrage du bot CubeGuardian")
            self.start_time = asyncio.get_event_loop().time()
            
            # Connexion Discord
            discord_token = self.config_manager.get_config('discord.discord.token')
            if not discord_token:
                self.logger.error("Token Discord manquant")
                return
            
            await super().start(discord_token)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage du bot: {e}")
            await self.message_manager.send_admin_alert("bot_startup_failed", {"error": str(e)})
    
    async def close(self) -> None:
        """Arrête proprement le bot"""
        try:
            self.logger.info("Arrêt du bot CubeGuardian")
            
            # Arrêter la surveillance
            await self.voice_monitor.stop_monitoring()
            
            # Fermer la connexion Discord
            await super().close()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt du bot: {e}")
    
    async def on_ready(self) -> None:
        """Événement déclenché quand le bot est prêt"""
        try:
            self.logger.info(f"Bot connecté en tant que {self.user}")
            self.log_manager.log_discord_event('connect', f"Connecté en tant que {self.user}")
            
            # Configuration des salons et de l'admin
            await self._setup_discord_channels()
            
            # Démarrage de la surveillance
            await self.voice_monitor.start_monitoring()
            
            # Envoi du message de démarrage
            await self.message_manager.send_bot_started_message()
            
            # Notification admin
            if self.config_manager.get_config('discord.admin.dm_on_startup', True):
                await self.message_manager.send_admin_alert("bot_started", {
                    "bot_name": self.user.name,
                    "guilds": len(self.guilds),
                    "startup_time": self.start_time
                })
            
            self.logger.info("Bot CubeGuardian opérationnel")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation: {e}")
            await self.message_manager.send_admin_alert("bot_initialization_failed", {"error": str(e)})
    
    async def _setup_discord_channels(self) -> None:
        """Configure les salons Discord et l'utilisateur admin"""
        try:
            # Trouver les salons
            voice_channel_name = self.config_manager.get_config('discord.discord.channels.voice_channel')
            text_channel_name = self.config_manager.get_config('discord.discord.channels.text_channel')
            
            voice_channel = None
            text_channel = None
            
            for guild in self.guilds:
                # Chercher le salon vocal
                for channel in guild.voice_channels:
                    if channel.name == voice_channel_name:
                        voice_channel = channel
                        break
                
                # Chercher le salon textuel
                for channel in guild.text_channels:
                    if channel.name == text_channel_name:
                        text_channel = channel
                        break
                
                if voice_channel and text_channel:
                    break
            
            if not voice_channel:
                self.logger.error(f"Salon vocal '{voice_channel_name}' non trouvé")
                return
            
            if not text_channel:
                self.logger.error(f"Salon textuel '{text_channel_name}' non trouvé")
                return
            
            # Configurer les salons
            self.message_manager.set_channels(text_channel, voice_channel)
            
            # Configurer l'utilisateur admin
            admin_id = int(self.config_manager.get_config('discord.discord.admin.user_id'))
            admin_user = self.get_user(admin_id)
            if admin_user:
                self.message_manager.set_admin_user(admin_user)
                self.logger.info(f"Utilisateur admin configuré: {admin_user.name}")
            else:
                self.logger.warning(f"Utilisateur admin {admin_id} non trouvé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration des salons: {e}")
    
    async def on_message(self, message: discord.Message) -> None:
        """
        Handler pour traiter les messages avec configuration hybride
        Analyseur NLP pour commandes de redémarrage Minecraft
        """
        try:
            # Ignorer les messages du bot lui-même
            if message.author == self.user:
                return
            
            # Configuration hybride selon le type de canal
            if isinstance(message.channel, discord.DMChannel):
                # Messages privés : MODE PERMISSIF (pas besoin de mention)
                require_mention = False
                self.logger.info(f"Message privé de {message.author.name}: MODE PERMISSIF")
            else:
                # Salons publics : MODE STRICT (mention obligatoire)
                require_mention = True
                self.logger.debug(f"Message salon public de {message.author.name}: MODE STRICT")
            
            # Analyse de la commande avec protection appropriée
            result = self.command_parser.parse_command(
                message.content,
                bot_name="CubeGuardian",
                require_mention=require_mention,
                discord_message=message  # IMPORTANT: Passer l'objet message Discord
            )
            
            # Log de l'analyse (AMÉLIORATION DEBUG)
            channel_type = 'MP' if isinstance(message.channel, discord.DMChannel) else 'Public'
            if result.confidence >= 0.1:  # Log si score significatif
                self.logger.info(f"Commande analysée - Intent: {result.intent.value}, "
                                f"Confiance: {result.confidence:.2f}, Canal: {channel_type}, "
                                f"Mots-clés: {result.matched_keywords}")
            else:
                # Log même les scores faibles pour diagnostic
                self.logger.debug(f"Analyse message '{message.content[:50]}...' - "
                                 f"Intent: {result.intent.value}, Confiance: {result.confidence:.2f}, "
                                 f"Canal: {channel_type}, Mention requise: {require_mention}")
            
            # Traitement selon l'intention détectée
            if result.intent == CommandIntent.RESTART_MINECRAFT and result.confidence >= 0.5:
                await self.process_restart_command(message.author, result, message.channel)
            elif result.intent == CommandIntent.HELP and result.confidence >= 0.5:
                # Utiliser le message d'aide du CommandParser
                help_text = self.command_parser.get_help_response()
                await self.message_manager.send_help_message(message.channel, help_text)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message: {e}")

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """Gère les changements d'état vocal"""
        try:
            await self.voice_monitor.on_voice_state_update(member, before, after)
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion du changement d'état vocal: {e}")

    async def process_restart_command(self, user: discord.Member, command_result: CommandResult, channel) -> None:
        """
        Traite une commande de redémarrage Minecraft avec sécurité
        Workflow complet : permissions → cooldown → confirmation → exécution
        """
        try:
            self.logger.info(f"Traitement commande redémarrage de {user.name} (confiance: {command_result.confidence:.2f})")
            
            # 1. Vérification permissions utilisateur
            if not self.user_manager.is_authorized(user.id):
                self.logger.warning(f"Utilisateur {user.name} (ID: {user.id}) non autorisé pour les commandes")
                await self.message_manager.send_permission_denied(channel, user)
                
                # Alerte admin si tentative non autorisée + enregistrement sécurité
                await self.message_manager.send_admin_alert("unauthorized_command_attempt", {
                    "user_name": user.name,
                    "user_id": user.id,
                    "command": getattr(command_result, 'command_text', 'N/A'),
                    "channel_type": "MP" if isinstance(channel, discord.DMChannel) else "Public"
                })
                
                # Enregistrer la tentative dans le système de sécurité
                self.security_manager._record_security_event(
                    user.id, "unauthorized_attempt", time.time(),
                    {"user_name": user.name, "command": str(command_result)[:100]},
                    "MEDIUM"  # Utiliser directement la string
                )
                return
            
            # 2. PROTECTION ANTI-SPAM : Vérifier si un redémarrage est déjà en cours
            if self.minecraft_manager.restart_in_progress:
                await channel.send("⚠️ **Redémarrage déjà en cours**\nUn redémarrage est actuellement en cours. Veuillez patienter.")
                self.logger.warning(f"Redémarrage déjà en cours - Demande de {user.name} rejetée")
                return
            
            # 2.1 PROTECTION CONFIRMATION : Vérifier les confirmations en attente
            current_time = time.time()
            expired_users = [uid for uid, timestamp in self.minecraft_manager.pending_confirmations.items() 
                           if current_time - timestamp > 60]  # 60s timeout
            for uid in expired_users:
                del self.minecraft_manager.pending_confirmations[uid]
            
            if user.id in self.minecraft_manager.pending_confirmations:
                await channel.send("⚠️ **Demande en attente**\nVous avez déjà une demande de confirmation en cours. Répondez d'abord à la précédente.")
                self.logger.warning(f"Confirmation déjà en attente pour {user.name}")
                return
            
            # 2.2 Vérification cooldown utilisateur (10 minutes)
            spam_result = self.minecraft_manager.check_user_cooldown(user.id)
            if not spam_result['allowed']:
                cooldown_remaining = spam_result['remaining_time']
                await channel.send(f"⏱️ **Cooldown actif**\nVous devez attendre encore **{cooldown_remaining}s** avant de pouvoir redémarrer à nouveau.\n\n*Limite: 1 redémarrage toutes les 10 minutes*")
                self.logger.warning(f"Cooldown actif pour {user.name}: {cooldown_remaining}s restantes")
                return
            
            # 2.3 MARQUER la demande comme en cours AVANT confirmation
            self.minecraft_manager.pending_confirmations[user.id] = current_time
            
            # 3. Demande de confirmation avec message_manager
            self.logger.info(f"Utilisateur {user.name} autorisé - Demande de confirmation requise")
            
            confirmed = await self.message_manager.send_restart_confirmation(channel, user, self, timeout=60)
            if not confirmed:
                # NETTOYER si annulé ou timeout
                if user.id in self.minecraft_manager.pending_confirmations:
                    del self.minecraft_manager.pending_confirmations[user.id]
                self.logger.info(f"Redémarrage annulé ou timeout pour {user.name}")
                return
            
            # 4. Progression du redémarrage
            await self.message_manager.send_restart_progress(channel)
            
            # 5. Exécution du redémarrage avec MinecraftManager
            success = await self.minecraft_manager.restart_minecraft_server(user, channel)
            if success.get('success', False):
                elapsed_time = success.get('elapsed_time', 0)
                await self.message_manager.send_restart_success(channel, elapsed_time)
                self.logger.info(f"Redémarrage Minecraft réussi en {elapsed_time}s pour {user.name}")
            else:
                error_type = success.get('error', 'unknown')
                error_details = success.get('details', 'Erreur inconnue')
                
                # Erreurs techniques (API, timeout, etc.) - plus d'erreurs de spam ici
                await self.message_manager.send_restart_failed(channel)
                self.logger.error(f"Échec redémarrage Minecraft pour {user.name}: {error_details}")
                
                # Alerte admin pour les erreurs techniques
                await self.message_manager.send_admin_alert("minecraft_restart_failed", {
                    "user_name": user.name,
                    "user_id": user.id,
                    "error": error_type,
                    "details": error_details
                })
            
            # Log de la commande traitée
            self.logger.info(f"Commande redémarrage complète pour {user.name} - "
                           f"Mots détectés: {command_result.matched_keywords}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la commande de redémarrage: {e}")
            await self.message_manager.send_admin_alert("restart_command_error", {
                "user_name": user.name,
                "user_id": user.id,
                "error": str(e)
            })
            
            # Enregistrer l'erreur dans le système de sécurité
            self.security_manager._record_security_event(
                user.id, "command_error", time.time(),
                {"error": str(e), "user_name": user.name},
                "HIGH"  # Utiliser directement la string
            )
    
    async def _on_authorized_user_join(self, user: discord.Member) -> None:
        """
        Callback appelé quand un utilisateur autorisé rejoint
        
        Args:
            user: Utilisateur qui a rejoint
        """
        try:
            self.logger.info(f"Utilisateur autorisé rejoint: {user.display_name}")
            self.logger.info(f"État actuel du bot: {self.state}")
            
            # Vérifier l'état du serveur
            if self.state == BotState.IDLE:
                self.logger.info("État IDLE détecté - Démarrage du serveur demandé")
                await self._request_server_startup(user)
            elif self.state == BotState.SHUTDOWN_TIMER:
                # Le timer sera annulé automatiquement par le voice_monitor
                self.logger.info("Timer d'arrêt annulé par l'arrivée d'un utilisateur autorisé")
            else:
                self.logger.info(f"État du bot: {self.state} - Aucune action requise")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion de l'arrivée d'utilisateur: {e}")
    
    async def _on_authorized_user_leave(self, user: discord.Member) -> None:
        """
        Callback appelé quand un utilisateur autorisé quitte
        
        Args:
            user: Utilisateur qui a quitté
        """
        try:
            self.logger.info(f"Utilisateur autorisé quitte: {user.display_name}")
            
            # Vérifier s'il reste des utilisateurs autorisés
            users_count = await self.voice_monitor.check_authorized_users()
            
            if users_count == 0 and self.state == BotState.SERVER_OPERATIONAL:
                self.logger.info("Aucun utilisateur autorisé restant - démarrage du timer d'arrêt de 10 minutes")
                await self._start_shutdown_timer()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion du départ d'utilisateur: {e}")

    async def _start_shutdown_timer(self) -> None:
        """Démarre le timer d'arrêt de 10 minutes avec possibilité d'interruption"""
        try:
            self.state = BotState.SHUTDOWN_TIMER
            self.logger.info("Démarrage du timer d'arrêt de 10 minutes")
            
            # Message d'arrêt dans 10 minutes
            await self.message_manager.send_shutdown_message(10)
            
            # Timer de 10 minutes avec vérification d'interruption
            for minute in range(10, 0, -1):
                await asyncio.sleep(60)  # Attendre 1 minute
                
                # Vérifier si quelqu'un a rejoint (interruption du timer)
                users_count = await self.voice_monitor.check_authorized_users()
                if users_count > 0:
                    self.logger.info("Timer d'arrêt annulé - utilisateur autorisé détecté")
                    self.state = BotState.SERVER_OPERATIONAL
                    # Pas de message spécifique, juste un log
                    self.logger.info("Message d'annulation d'arrêt envoyé")
                    return
                
                # Message de compte à rebours
                if minute > 1:
                    self.logger.info(f"Arrêt dans {minute - 1} minute(s)")
                    # Pas de message Discord pour éviter le spam, juste un log
            
            # Timer expiré - procéder à l'arrêt
            await self._execute_shutdown()
            
        except Exception as e:
            self.logger.error(f"Erreur lors du timer d'arrêt: {e}")
            self.state = BotState.ERROR
            await self.message_manager.send_admin_alert("shutdown_timer_error", {"error": str(e)})

    async def _execute_shutdown(self) -> None:
        """Exécute l'arrêt du serveur avec surveillance"""
        try:
            self.logger.info("Exécution de l'arrêt du serveur")
            self.state = BotState.SHUTDOWN_IN_PROGRESS
            
            # Message d'arrêt en cours
            await self.message_manager.send_shutdown_progress_message()
            
            # Arrêter le nœud Proxmox
            success = await self.server_manager.shutdown_server()
            
            if not success:
                self.logger.error("Échec de la commande d'arrêt")
                await self.message_manager.send_shutdown_failed_message()
                await self.message_manager.send_admin_alert("shutdown_failed", {
                    "reason": "Échec de la commande d'arrêt"
                })
                self.state = BotState.ERROR
                return
            
            # Surveiller l'arrêt pendant 10 minutes
            await self._monitor_shutdown_progress()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'arrêt: {e}")
            self.state = BotState.ERROR
            await self.message_manager.send_admin_alert("shutdown_execution_error", {"error": str(e)})

    async def _monitor_shutdown_progress(self) -> None:
        """Surveille l'arrêt du serveur toutes les minutes"""
        max_attempts = 10  # 10 minutes maximum
        attempt = 0
        start_time = asyncio.get_event_loop().time()
        
        while attempt < max_attempts and self.state == BotState.SHUTDOWN_IN_PROGRESS:
            attempt += 1
            self.logger.info(f"Tentative {attempt}/{max_attempts} - Vérification de l'arrêt")
            
            # Attendre 1 minute
            await asyncio.sleep(60)
            
            # Vérifier si on est toujours en mode arrêt
            if self.state != BotState.SHUTDOWN_IN_PROGRESS:
                return
            
            # Test Proxmox (doit être DOWN)
            proxmox_result = await self.server_manager.check_proxmox_status()
            if not proxmox_result['success']:
                # Serveur arrêté !
                elapsed_time = int(asyncio.get_event_loop().time() - start_time)
                self.state = BotState.IDLE
                self.logger.info(f"Serveur arrêté en {elapsed_time} secondes")
                await self.message_manager.send_shutdown_success_message(elapsed_time)
                return
            
            self.logger.info(f"Tentative {attempt}: Serveur toujours en ligne, attente...")
        
        # Échec après 10 minutes
        self.state = BotState.ERROR
        self.logger.error("Échec de l'arrêt après 10 minutes")
        await self.message_manager.send_shutdown_failed_message()
        await self.message_manager.send_admin_alert("shutdown_failed", {
            "reason": "Timeout après 10 minutes",
            "timeout_minutes": 10
        })
    
    
    async def _on_shutdown_timer_cancelled(self, user: discord.Member) -> None:
        """
        Callback appelé quand le timer d'arrêt est annulé
        
        Args:
            user: Utilisateur qui a annulé l'arrêt
        """
        try:
            self.logger.info(f"Timer d'arrêt annulé par {user.display_name}")
            self.state = BotState.SERVER_OPERATIONAL
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'annulation du timer: {e}")
    
    async def _request_server_startup(self, user: discord.Member) -> None:
        """
        Nouveau workflow de démarrage optimisé
        
        Args:
            user: Utilisateur qui a demandé le démarrage
        """
        try:
            self.logger.info(f"Démarrage du serveur demandé par {user.display_name}")
            
            # 1. Vérifier immédiatement si Minecraft est déjà UP
            self.logger.info("Étape 1: Vérification de la connectivité Minecraft...")
            minecraft_result = await self.server_manager.check_minecraft_status()
            self.logger.info(f"Résultat test Minecraft: {minecraft_result}")
            
            if minecraft_result['success']:
                # Minecraft déjà opérationnel !
                self.state = BotState.SERVER_OPERATIONAL
                self.logger.info("Minecraft déjà opérationnel !")
                await self.message_manager.send_server_already_operational_message()
                return
            
            # 2. Minecraft n'est pas UP, signaler le démarrage
            self.logger.info("Étape 2: Minecraft non accessible - Signalement du démarrage...")
            self.state = BotState.STARTUP_REQUESTED
            await self.message_manager.send_startup_message(user)
            
            # 3. Envoyer Wake-on-LAN
            self.logger.info("Étape 3: Envoi du Wake-on-LAN...")
            wake_result = await self.server_manager.wake_server()
            self.logger.info(f"Résultat Wake-on-LAN: {wake_result}")
            
            # Gérer le cas où wake_result est un booléen (interface) ou un dictionnaire (manager natif)
            if isinstance(wake_result, bool):
                # Interface retourne un booléen
                if wake_result:
                    self.logger.info("Wake-on-LAN envoyé avec succès")
                else:
                    self.logger.warning("Wake-on-LAN échoué, mais on continue la surveillance")
                    # Envoyer un message d'erreur dans le salon textuel
                    await self.message_manager.send_error_message("wake_on_lan_failed", {
                        "target_host": "192.168.1.245",
                        "error": "Échec du Wake-on-LAN"
                    })
            else:
                # Manager natif retourne un dictionnaire
                if wake_result.get('success', False):
                    self.logger.info("Wake-on-LAN envoyé avec succès")
                else:
                    self.logger.warning("Wake-on-LAN échoué, mais on continue la surveillance")
                    # Envoyer un message d'erreur dans le salon textuel
                    await self.message_manager.send_error_message("wake_on_lan_failed", {
                        "target_host": wake_result.get('details', {}).get('target_host', 'Serveur inconnu'),
                        "error": wake_result.get('error', 'Erreur inconnue')
                    })
            
            # 4. Passer en mode surveillance avec timer
            self.state = BotState.STARTUP_MONITORING
            await self.message_manager.send_startup_progress_message()
            
            # 5. Surveillance toutes les minutes pendant 10 minutes
            start_time = asyncio.get_event_loop().time()
            await self._monitor_startup_progress(start_time)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage du serveur: {e}")
            self.state = BotState.ERROR
            await self.message_manager.send_admin_alert("startup_failed", {"error": str(e)})

    async def _monitor_startup_progress(self, start_time: float) -> None:
        """Surveille le démarrage du serveur toutes les minutes"""
        max_attempts = 10  # 10 minutes maximum
        attempt = 0
        
        while attempt < max_attempts and self.state == BotState.STARTUP_MONITORING:
            attempt += 1
            self.logger.info(f"Tentative {attempt}/{max_attempts} - Vérification du démarrage")
            
            # Attendre 1 minute
            await asyncio.sleep(60)
            
            # Vérifier si on est toujours en mode surveillance
            if self.state != BotState.STARTUP_MONITORING:
                return
            
            # Test Proxmox
            proxmox_result = await self.server_manager.check_proxmox_status()
            if not proxmox_result['success']:
                self.logger.info(f"Tentative {attempt}: Proxmox pas encore UP")
                continue
            
            self.logger.info(f"Tentative {attempt}: Proxmox UP, test Minecraft...")
            
            # Test Minecraft
            minecraft_result = await self.server_manager.check_minecraft_status()
            if minecraft_result['success']:
                # Succès !
                elapsed_time = int(asyncio.get_event_loop().time() - start_time)
                self.state = BotState.SERVER_OPERATIONAL
                self.logger.info(f"Minecraft opérationnel en {elapsed_time} secondes !")
                minecraft_config = self.server_manager.minecraft_config
                await self.message_manager.send_startup_success_message(elapsed_time)
                return
        
        # Échec après 10 minutes
        self.state = BotState.ERROR
        self.logger.error("Échec du démarrage après 10 minutes")
        await self.message_manager.send_startup_failed_message(10)
        await self.message_manager.send_admin_alert("startup_failed", {
            "reason": "Timeout après 10 minutes",
            "timeout_minutes": 10
        })
    
    def get_state(self) -> BotState:
        """
        Récupère l'état actuel du bot
        
        Returns:
            État actuel du bot
        """
        return self.state
    
    def set_state(self, state: BotState) -> bool:
        """
        Définit l'état du bot
        
        Args:
            state: Nouvel état
            
        Returns:
            True si l'état a été défini avec succès
        """
        try:
            old_state = self.state
            self.state = state
            self.logger.info(f"Changement d'état: {old_state.value} -> {state.value}")
            self.log_manager.log_bot_state_change(old_state.value, state.value)
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors du changement d'état: {e}")
            return False
    
    async def _security_cleanup_task(self) -> None:
        """Tâche de nettoyage automatique des données de sécurité"""
        try:
            while True:
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
                if hasattr(self, 'security_manager'):
                    self.security_manager.cleanup_old_data()
                    self.logger.debug("Nettoyage automatique des données de sécurité effectué")
        except asyncio.CancelledError:
            self.logger.info("Tâche de nettoyage sécurité arrêtée")
        except Exception as e:
            self.logger.error(f"Erreur dans la tâche de nettoyage sécurité: {e}")

    def get_bot_info(self) -> dict:
        """
        Récupère les informations du bot avec statistiques de sécurité
        
        Returns:
            Dictionnaire avec les informations du bot
        """
        uptime = 0
        if self.start_time:
            uptime = asyncio.get_event_loop().time() - self.start_time
        
        info = {
            'name': self.user.name if self.user else 'Non connecté',
            'id': self.user.id if self.user else None,
            'state': self.state.value,
            'uptime_seconds': uptime,
            'guilds_count': len(self.guilds),
            'voice_monitor_status': self.voice_monitor.get_monitoring_status(),
            'server_status': self.server_manager.get_server_status(),
            'user_statistics': self.user_manager.get_statistics()
        }
        
        # Ajouter les statistiques de sécurité si disponibles
        try:
            if hasattr(self, 'security_manager'):
                info['security_statistics'] = self.security_manager.get_security_statistics()
            if hasattr(self, 'minecraft_manager'):
                info['minecraft_statistics'] = self.minecraft_manager.get_minecraft_statistics()
        except Exception as e:
            self.logger.warning(f"Erreur lors de la récupération des statistiques: {e}")
            
        return info
    
    async def on_error(self, event: str, *args, **kwargs) -> None:
        """Gère les erreurs du bot"""
        self.logger.error(f"Erreur dans l'événement {event}: {args}, {kwargs}")
        await self.message_manager.send_admin_alert("bot_error", {
            "event": event,
            "args": str(args),
            "kwargs": str(kwargs)
        })

async def main():
    """Fonction principale"""
    try:
        # Création du bot
        bot = CubeGuardianBot()
        
        # Démarrage du bot
        await bot.start()
        
    except KeyboardInterrupt:
        print("Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
        # Configuration du logging pour le script principal - MODE DEBUG ACTIVÉ
    logging.basicConfig(
        level=logging.DEBUG,  # CHANGEMENT: Passer en DEBUG pour diagnostic
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Lancement du bot
    asyncio.run(main())
