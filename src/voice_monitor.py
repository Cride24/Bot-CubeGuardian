"""
Surveillance vocale pour Bot CubeGuardian
Surveillance des salons vocaux Discord et gestion des événements
"""

import asyncio
import logging
from typing import Optional, Set, List
from datetime import datetime
import discord

class VoiceMonitor:
    """Surveillance des salons vocaux Discord"""
    
    def __init__(self, bot, config_manager, user_manager, message_manager, log_manager):
        """
        Initialise le surveillant vocal
        
        Args:
            bot: Instance du bot Discord
            config_manager: Gestionnaire de configuration
            user_manager: Gestionnaire d'utilisateurs
            message_manager: Gestionnaire de messages
            log_manager: Gestionnaire de logs
        """
        self.bot = bot
        self.config_manager = config_manager
        self.user_manager = user_manager
        self.message_manager = message_manager
        self.log_manager = log_manager
        self.logger = logging.getLogger('CubeGuardian.VoiceMonitor')
        
        # Configuration
        self.voice_channel_name = self.config_manager.get_config('discord.channels.voice_channel', "L'écho-du-Cube")
        self.shutdown_delay = self.config_manager.get_timer('shutdown_delay')
        
        # État de surveillance
        self.monitored_channel = None
        self.authorized_users_present = set()
        self.shutdown_timer = None
        self.monitoring_active = False
        
        # Callbacks pour les événements
        self.on_user_join_callback = None
        self.on_user_leave_callback = None
        self.on_timer_expired_callback = None
        self.on_timer_cancelled_callback = None
        
        self.logger.info(f"VoiceMonitor initialisé pour le salon: {self.voice_channel_name}")
    
    def set_callbacks(self, on_user_join=None, on_user_leave=None, on_timer_expired=None, on_timer_cancelled=None):
        """
        Définit les callbacks pour les événements
        
        Args:
            on_user_join: Callback appelé quand un utilisateur autorisé rejoint
            on_user_leave: Callback appelé quand un utilisateur autorisé quitte
            on_timer_expired: Callback appelé quand le timer d'arrêt expire
            on_timer_cancelled: Callback appelé quand le timer d'arrêt est annulé
        """
        self.on_user_join_callback = on_user_join
        self.on_user_leave_callback = on_user_leave
        self.on_timer_expired_callback = on_timer_expired
        self.on_timer_cancelled_callback = on_timer_cancelled
        
        self.logger.info("Callbacks définis pour VoiceMonitor")
    
    async def start_monitoring(self) -> None:
        """Démarre la surveillance du salon vocal"""
        try:
            # Trouver le salon vocal
            self.monitored_channel = await self._find_voice_channel()
            
            if not self.monitored_channel:
                self.logger.error(f"Salon vocal '{self.voice_channel_name}' non trouvé")
                return
            
            # Initialiser l'état des utilisateurs présents
            await self._update_authorized_users_present()
            
            self.monitoring_active = True
            self.logger.info(f"Surveillance démarrée pour le salon: {self.monitored_channel.name}")
            self.log_manager.log_voice_event('monitoring_started', 'Bot', self.monitored_channel.name)
            
            # Envoyer le message de surveillance active
            await self.message_manager.send_monitoring_active_message(self.monitored_channel.name)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage de la surveillance: {e}")
            self.monitoring_active = False
    
    async def stop_monitoring(self) -> None:
        """Arrête la surveillance du salon vocal"""
        try:
            self.monitoring_active = False
            
            # Annuler le timer d'arrêt s'il est actif
            if self.shutdown_timer:
                self.shutdown_timer.cancel()
                self.shutdown_timer = None
            
            self.logger.info("Surveillance arrêtée")
            self.log_manager.log_voice_event('monitoring_stopped', 'Bot')
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt de la surveillance: {e}")
    
    async def _find_voice_channel(self) -> Optional[discord.VoiceChannel]:
        """
        Trouve le salon vocal à surveiller
        
        Returns:
            Salon vocal Discord ou None
        """
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                if channel.name == self.voice_channel_name:
                    return channel
        
        return None
    
    async def _update_authorized_users_present(self) -> None:
        """Met à jour la liste des utilisateurs autorisés présents"""
        if not self.monitored_channel:
            return
        
        current_users = set()
        
        for member in self.monitored_channel.members:
            if self.user_manager.is_authorized(member.id):
                current_users.add(member.id)
                # Mettre à jour la présence dans le user manager
                self.user_manager.update_user_presence(member.id, True)
        
        # Identifier les utilisateurs qui ont quitté
        users_left = self.authorized_users_present - current_users
        for user_id in users_left:
            self.user_manager.update_user_presence(user_id, False)
        
        # Identifier les utilisateurs qui ont rejoint
        users_joined = current_users - self.authorized_users_present
        
        # Mettre à jour la liste
        self.authorized_users_present = current_users
        
        # Traiter les événements
        for user_id in users_joined:
            await self._handle_user_join(user_id)
        
        for user_id in users_left:
            await self._handle_user_leave(user_id)
    
    async def _handle_user_join(self, user_id: int) -> None:
        """
        Gère l'arrivée d'un utilisateur autorisé
        
        Args:
            user_id: ID de l'utilisateur qui a rejoint
        """
        try:
            user = self.bot.get_user(user_id)
            if not user:
                self.logger.warning(f"Utilisateur {user_id} non trouvé")
                return
            
            self.logger.info(f"Utilisateur autorisé rejoint: {user.display_name}")
            self.log_manager.log_voice_event('join', user.display_name, self.monitored_channel.name)
            
            # Annuler le timer d'arrêt s'il est actif
            if self.shutdown_timer:
                self.shutdown_timer.cancel()
                self.shutdown_timer = None
                self.logger.info("Timer d'arrêt annulé - utilisateur autorisé détecté")
                
                # Envoyer le message d'annulation
                await self.message_manager.send_shutdown_cancelled_message(user)
                
                # Appeler le callback
                if self.on_timer_cancelled_callback:
                    await self.on_timer_cancelled_callback(user)
            
            # Envoyer le message d'arrivée
            await self.message_manager.send_user_joined_message(user)
            
            # Appeler le callback
            if self.on_user_join_callback:
                await self.on_user_join_callback(user)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion de l'arrivée de l'utilisateur {user_id}: {e}")
    
    async def _handle_user_leave(self, user_id: int) -> None:
        """
        Gère le départ d'un utilisateur autorisé
        
        Args:
            user_id: ID de l'utilisateur qui a quitté
        """
        try:
            user = self.bot.get_user(user_id)
            if not user:
                self.logger.warning(f"Utilisateur {user_id} non trouvé")
                return
            
            self.logger.info(f"Utilisateur autorisé quitte: {user.display_name}")
            self.log_manager.log_voice_event('leave', user.display_name, self.monitored_channel.name)
            
            # Envoyer le message de départ
            await self.message_manager.send_user_left_message(user)
            
            # Vérifier s'il reste des utilisateurs autorisés
            if not self.authorized_users_present:
                self.logger.info("Aucun utilisateur autorisé restant - démarrage du timer d'arrêt")
                await self.start_shutdown_timer()
            
            # Appeler le callback
            if self.on_user_leave_callback:
                await self.on_user_leave_callback(user)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion du départ de l'utilisateur {user_id}: {e}")
    
    async def start_shutdown_timer(self) -> None:
        """Démarre le timer d'arrêt du serveur"""
        try:
            if self.shutdown_timer:
                self.logger.warning("Timer d'arrêt déjà actif")
                return
            
            self.logger.info(f"Démarrage du timer d'arrêt ({self.shutdown_delay} secondes)")
            
            # Ne pas envoyer de message ici - laisser le Bot gérer l'arrêt
            # Le Bot enverra son propre message avec le timer de 10 minutes
            
            # Créer le timer
            self.shutdown_timer = asyncio.create_task(self._shutdown_timer_task())
            
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage du timer d'arrêt: {e}")
    
    async def cancel_shutdown_timer(self) -> None:
        """Annule le timer d'arrêt du serveur"""
        try:
            if self.shutdown_timer:
                self.shutdown_timer.cancel()
                self.shutdown_timer = None
                self.logger.info("Timer d'arrêt annulé")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'annulation du timer d'arrêt: {e}")
    
    async def _shutdown_timer_task(self) -> None:
        """Tâche du timer d'arrêt"""
        try:
            # Attendre le délai d'arrêt
            await asyncio.sleep(self.shutdown_delay)
            
            # Vérifier qu'il n'y a toujours pas d'utilisateurs autorisés
            await self._update_authorized_users_present()
            
            if not self.authorized_users_present:
                self.logger.info("Timer d'arrêt expiré - aucun utilisateur autorisé détecté")
                self.log_manager.log_voice_event('timer_expired', 'Bot')
                
                # Appeler le callback
                if self.on_timer_expired_callback:
                    await self.on_timer_expired_callback()
            else:
                self.logger.info("Timer d'arrêt expiré mais utilisateurs autorisés détectés - arrêt annulé")
            
            self.shutdown_timer = None
            
        except asyncio.CancelledError:
            self.logger.info("Timer d'arrêt annulé")
            self.shutdown_timer = None
        except Exception as e:
            self.logger.error(f"Erreur dans la tâche du timer d'arrêt: {e}")
            self.shutdown_timer = None
    
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """
        Gère les changements d'état vocal
        
        Args:
            member: Membre Discord
            before: État vocal précédent
            after: État vocal actuel
        """
        if not self.monitoring_active or not self.monitored_channel:
            return
        
        try:
            # Vérifier si le changement concerne notre salon
            if (before.channel != self.monitored_channel and 
                after.channel != self.monitored_channel):
                return
            
            # Mettre à jour la liste des utilisateurs présents
            await self._update_authorized_users_present()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion du changement d'état vocal: {e}")
    
    async def check_authorized_users(self) -> int:
        """
        Compte les utilisateurs autorisés présents
        
        Returns:
            Nombre d'utilisateurs autorisés présents
        """
        if not self.monitored_channel:
            return 0
        
        count = 0
        for member in self.monitored_channel.members:
            if self.user_manager.is_authorized(member.id):
                count += 1
        
        return count
    
    def get_monitoring_status(self) -> dict:
        """
        Récupère le statut de la surveillance
        
        Returns:
            Dictionnaire avec le statut
        """
        return {
            'monitoring_active': self.monitoring_active,
            'monitored_channel': {
                'name': self.monitored_channel.name if self.monitored_channel else None,
                'id': self.monitored_channel.id if self.monitored_channel else None
            },
            'authorized_users_present': len(self.authorized_users_present),
            'shutdown_timer_active': self.shutdown_timer is not None,
            'shutdown_delay': self.shutdown_delay
        }
    
    def get_authorized_users_present(self) -> List[int]:
        """
        Récupère la liste des utilisateurs autorisés présents
        
        Returns:
            Liste des IDs des utilisateurs autorisés présents
        """
        return list(self.authorized_users_present)
    
    def is_shutdown_timer_active(self) -> bool:
        """
        Vérifie si le timer d'arrêt est actif
        
        Returns:
            True si le timer d'arrêt est actif
        """
        return self.shutdown_timer is not None
    
    def __str__(self) -> str:
        """Représentation string du surveillant vocal"""
        channel_name = self.monitored_channel.name if self.monitored_channel else "Non défini"
        users_count = len(self.authorized_users_present)
        timer_status = "Actif" if self.shutdown_timer else "Inactif"
        
        return f"VoiceMonitor(channel={channel_name}, users={users_count}, timer={timer_status})"
