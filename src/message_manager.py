"""
Gestionnaire de messages pour Bot CubeGuardian
Gestion des messages Discord et des notifications
"""

import discord
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

class MessageManager:
    """Gestionnaire des messages et notifications Discord"""
    
    def __init__(self, config_manager, log_manager):
        """
        Initialise le gestionnaire de messages
        
        Args:
            config_manager: Gestionnaire de configuration
            log_manager: Gestionnaire de logs
        """
        self.config_manager = config_manager
        self.log_manager = log_manager
        self.logger = logging.getLogger('CubeGuardian.MessageManager')
        
        # Salons Discord
        self.text_channel = None
        self.voice_channel = None
        
        # Utilisateur admin
        self.admin_user = None
        
        # Messages en attente (pour éviter le spam)
        self.pending_messages = []
        
        self.logger.info("MessageManager initialisé")
    
    def set_channels(self, text_channel: discord.TextChannel, voice_channel: discord.VoiceChannel) -> None:
        """
        Définit les salons Discord
        
        Args:
            text_channel: Salon textuel
            voice_channel: Salon vocal
        """
        self.text_channel = text_channel
        self.voice_channel = voice_channel
        self.logger.info(f"Salons définis: textuel={text_channel.name}, vocal={voice_channel.name}")
    
    def set_admin_user(self, admin_user: discord.User) -> None:
        """
        Définit l'utilisateur administrateur
        
        Args:
            admin_user: Utilisateur administrateur
        """
        self.admin_user = admin_user
        self.logger.info(f"Utilisateur admin défini: {admin_user.name}")
    
    def format_message(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Formate un message avec des variables
        
        Args:
            template: Template du message
            variables: Variables pour le formatage
            
        Returns:
            Message formaté
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            self.logger.warning(f"Variable manquante dans le template: {e}")
            return template
        except Exception as e:
            self.logger.error(f"Erreur lors du formatage du message: {e}")
            return template
    
    async def send_startup_message(self, user: discord.Member) -> None:
        """
        Envoie un message de démarrage du serveur
        
        Args:
            user: Utilisateur qui a demandé le démarrage
        """
        if not self.text_channel:
            self.logger.warning("Salon textuel non défini, impossible d'envoyer le message de démarrage")
            return
        
        try:
            message = self.config_manager.get_message('startup.request', user=user.display_name)
            await self.text_channel.send(message)
            self.logger.info(f"Message de démarrage envoyé pour {user.display_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de démarrage: {e}")
    
    async def send_startup_progress_message(self) -> None:
        """Envoie un message de progression du démarrage"""
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('startup.in_progress')
            await self.text_channel.send(message)
            self.logger.info("Message de progression du démarrage envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de progression: {e}")
    
    async def send_startup_success_message(self, elapsed_time: int) -> None:
        """
        Envoie un message de succès du démarrage avec le temps écoulé
        
        Args:
            elapsed_time: Temps écoulé en secondes
        """
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('startup.success')
            formatted_message = message.format(time=elapsed_time)
            await self.text_channel.send(formatted_message)
            self.logger.info(f"Message de succès du démarrage envoyé (temps: {elapsed_time}s)")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de succès: {e}")
    
    async def send_startup_failed_message(self, timeout: int) -> None:
        """
        Envoie un message d'échec du démarrage
        
        Args:
            timeout: Timeout atteint en minutes
        """
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('startup.failed', timeout=timeout)
            await self.text_channel.send(message)
            self.logger.info("Message d'échec du démarrage envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'échec: {e}")
    
    async def send_server_already_operational_message(self) -> None:
        """Envoie un message indiquant que le serveur est déjà opérationnel"""
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('startup.already_operational')
            await self.text_channel.send(message)
            self.logger.info("Message 'serveur déjà opérationnel' envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message 'serveur déjà opérationnel': {e}")
    
    async def send_shutdown_message(self, delay: int) -> None:
        """
        Envoie un message d'arrêt programmé
        
        Args:
            delay: Délai en minutes avant l'arrêt
        """
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('shutdown.initiated', delay=delay)
            await self.text_channel.send(message)
            self.logger.info(f"Message d'arrêt programmé envoyé (délai: {delay}min)")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'arrêt: {e}")
    
    async def send_shutdown_cancelled_message(self, user: discord.Member) -> None:
        """
        Envoie un message d'annulation d'arrêt
        
        Args:
            user: Utilisateur qui a annulé l'arrêt
        """
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('shutdown.cancelled', user=user.display_name)
            await self.text_channel.send(message)
            self.logger.info(f"Message d'annulation d'arrêt envoyé pour {user.display_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'annulation: {e}")
    
    async def send_shutdown_progress_message(self) -> None:
        """Envoie un message de progression de l'arrêt"""
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('shutdown.in_progress')
            await self.text_channel.send(message)
            self.logger.info("Message de progression de l'arrêt envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de progression d'arrêt: {e}")
    
    async def send_shutdown_success_message(self, elapsed_time: int) -> None:
        """Envoie un message de succès de l'arrêt avec le temps écoulé"""
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('shutdown.confirmed')
            formatted_message = message.format(time=elapsed_time)
            await self.text_channel.send(formatted_message)
            self.logger.info(f"Message de succès de l'arrêt envoyé (temps: {elapsed_time}s)")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de succès d'arrêt: {e}")
    
    async def send_shutdown_failed_message(self) -> None:
        """Envoie un message d'échec de l'arrêt"""
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('shutdown.failed')
            await self.text_channel.send(message)
            self.logger.info("Message d'échec de l'arrêt envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'échec d'arrêt: {e}")
    
    async def send_user_joined_message(self, user: discord.Member) -> None:
        """
        Envoie un message d'arrivée d'utilisateur
        
        Args:
            user: Utilisateur qui a rejoint
        """
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('info.user_joined', user=user.display_name)
            await self.text_channel.send(message)
            self.logger.info(f"Message d'arrivée envoyé pour {user.display_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'arrivée: {e}")
    
    async def send_user_left_message(self, user: discord.Member) -> None:
        """
        Envoie un message de départ d'utilisateur
        
        Args:
            user: Utilisateur qui a quitté
        """
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('info.user_left', user=user.display_name)
            await self.text_channel.send(message)
            self.logger.info(f"Message de départ envoyé pour {user.display_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de départ: {e}")
    
    async def send_bot_started_message(self) -> None:
        """Envoie un message de démarrage du bot"""
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('info.bot_started')
            await self.text_channel.send(message)
            self.logger.info("Message de démarrage du bot envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de démarrage du bot: {e}")
    
    async def send_monitoring_active_message(self, channel_name: str) -> None:
        """
        Envoie un message de surveillance active
        
        Args:
            channel_name: Nom du salon surveillé
        """
        if not self.text_channel:
            return
        
        try:
            message = self.config_manager.get_message('info.monitoring_active', channel=channel_name)
            await self.text_channel.send(message)
            self.logger.info(f"Message de surveillance active envoyé pour {channel_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de surveillance: {e}")
    
    async def send_admin_alert(self, alert_type: str, details: Dict[str, Any]) -> None:
        """
        Envoie une alerte à l'administrateur
        
        Args:
            alert_type: Type d'alerte
            details: Détails de l'alerte
        """
        if not self.admin_user:
            self.logger.warning("Utilisateur admin non défini, impossible d'envoyer l'alerte")
            return
        
        try:
            # Récupérer le message d'alerte
            message_template = self.config_manager.get_message(f'admin_alerts.{alert_type}')
            
            # Formater le message avec les détails
            message = self.format_message(message_template, details)
            
            # Créer un embed pour l'alerte
            embed = discord.Embed(
                title="🚨 Alerte CubeGuardian",
                description=message,
                color=0xff0000,  # Rouge
                timestamp=datetime.utcnow()
            )
            
            # Ajouter les détails dans les champs
            for key, value in details.items():
                embed.add_field(name=key, value=str(value), inline=True)
            
            # Envoyer l'alerte
            await self.admin_user.send(embed=embed)
            self.logger.info(f"Alerte admin envoyée: {alert_type}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'alerte admin: {e}")
    
    async def send_error_message(self, error_type: str, details: Dict[str, Any]) -> None:
        """
        Envoie un message d'erreur
        
        Args:
            error_type: Type d'erreur
            details: Détails de l'erreur
        """
        if not self.text_channel:
            return
        
        try:
            message_template = self.config_manager.get_message(f'errors.{error_type}')
            message = self.format_message(message_template, details)
            
            await self.text_channel.send(message)
            self.logger.info(f"Message d'erreur envoyé: {error_type}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'erreur: {e}")
    
    async def send_status_message(self, status: str, details: Dict[str, Any] = None) -> None:
        """
        Envoie un message de statut
        
        Args:
            status: Statut à afficher
            details: Détails supplémentaires
        """
        if not self.text_channel:
            return
        
        try:
            # Créer un embed pour le statut
            embed = discord.Embed(
                title="📊 Statut CubeGuardian",
                description=status,
                color=0x00ff00,  # Vert
                timestamp=datetime.utcnow()
            )
            
            # Ajouter les détails si fournis
            if details:
                for key, value in details.items():
                    embed.add_field(name=key, value=str(value), inline=True)
            
            await self.text_channel.send(embed=embed)
            self.logger.info(f"Message de statut envoyé: {status}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de statut: {e}")
    
    async def send_custom_message(self, message: str, channel: discord.TextChannel = None) -> None:
        """
        Envoie un message personnalisé
        
        Args:
            message: Message à envoyer
            channel: Salon où envoyer le message (par défaut: salon textuel)
        """
        target_channel = channel or self.text_channel
        
        if not target_channel:
            self.logger.warning("Aucun salon défini pour envoyer le message personnalisé")
            return
        
        try:
            await target_channel.send(message)
            self.logger.info("Message personnalisé envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message personnalisé: {e}")
    
    def get_channel_info(self) -> Dict[str, Any]:
        """
        Récupère les informations des salons
        
        Returns:
            Dictionnaire avec les informations des salons
        """
        return {
            'text_channel': {
                'name': self.text_channel.name if self.text_channel else None,
                'id': self.text_channel.id if self.text_channel else None
            },
            'voice_channel': {
                'name': self.voice_channel.name if self.voice_channel else None,
                'id': self.voice_channel.id if self.voice_channel else None
            },
            'admin_user': {
                'name': self.admin_user.name if self.admin_user else None,
                'id': self.admin_user.id if self.admin_user else None
            }
        }
    
    # ========================================
    # 🎮 NOUVELLES MÉTHODES - COMMANDES INTERACTIVES
    # ========================================

    async def send_restart_confirmation(self, channel, user: discord.Member, bot_client, timeout: int = 60) -> bool:
        """
        Envoie une demande de confirmation de redémarrage et attend la réponse
        
        Args:
            channel: Canal Discord (MP ou salon public)
            user: Utilisateur qui demande le redémarrage
            bot_client: Instance du bot Discord pour wait_for
            timeout: Délai d'attente en secondes (défaut: 60)
            
        Returns:
            True si confirmé, False sinon
        """
        try:
            # Message de confirmation selon le cahier des charges
            confirmation_message = (
                f"🤖 **Commande détectée : Redémarrage Minecraft**\n"
                f"⚠️ Cette action va redémarrer le serveur Minecraft et déconnecter tous les joueurs connectés.\n"
                f"**Êtes-vous sûr(e) de vouloir continuer ?**\n\n"
                f"Répondez par **oui** ou **non** dans les {timeout} secondes."
            )
            
            await channel.send(confirmation_message)
            self.logger.info(f"Demande de confirmation envoyée à {user.name}")
            
            # Attendre la réponse de l'utilisateur
            def check(message):
                return (message.author == user and 
                       message.channel == channel and 
                       message.content.lower().strip() in ['oui', 'yes', 'o', 'y', 'non', 'no', 'n'])
            
            import asyncio
            try:
                response = await bot_client.wait_for('message', check=check, timeout=timeout)
                user_response = response.content.lower().strip()
                
                if user_response in ['oui', 'yes', 'o', 'y']:
                    # Confirmation reçue
                    await channel.send(
                        f"✅ **Confirmation reçue**\n"
                        f"🔄 Redémarrage du serveur Minecraft en cours..."
                    )
                    self.logger.info(f"Confirmation reçue de {user.name}")
                    return True
                else:
                    # Annulation
                    await channel.send(
                        f"❌ **Redémarrage annulé**\n"
                        f"Aucune action n'a été effectuée."
                    )
                    self.logger.info(f"Redémarrage annulé par {user.name}")
                    return False
                    
            except asyncio.TimeoutError:
                # Timeout
                await channel.send(
                    f"⏰ **Délai d'attente dépassé**\n"
                    f"Redémarrage annulé par manque de confirmation."
                )
                self.logger.info(f"Timeout de confirmation pour {user.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la demande de confirmation: {e}")
            return False

    async def send_permission_denied(self, channel, user: discord.Member) -> None:
        """
        Envoie un message de permission refusée
        
        Args:
            channel: Canal Discord
            user: Utilisateur non autorisé
        """
        try:
            message = (
                f"🚫 **Permission refusée**\n"
                f"Seuls les joueurs autorisés peuvent exécuter cette commande."
            )
            
            await channel.send(message)
            self.logger.info(f"Permission refusée envoyée à {user.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du refus de permission: {e}")

    async def send_cooldown_message(self, channel, user: discord.Member, minutes_remaining: int) -> None:
        """
        Envoie un message de cooldown actif
        
        Args:
            channel: Canal Discord
            user: Utilisateur en cooldown
            minutes_remaining: Minutes restantes
        """
        try:
            message = (
                f"⏳ **Cooldown actif**\n"
                f"Vous devez attendre encore **{minutes_remaining} minutes** avant de pouvoir exécuter cette commande."
            )
            
            await channel.send(message)
            self.logger.info(f"Message de cooldown envoyé à {user.name} ({minutes_remaining} min)")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de cooldown: {e}")

    async def send_restart_progress(self, channel) -> None:
        """
        Envoie un message de progression du redémarrage
        
        Args:
            channel: Canal Discord
        """
        try:
            message = (
                f"🔄 **Redémarrage en cours...**\n"
                f"⏱️ Surveillance du processus - Maximum 5 minutes\n"
                f"📊 Statut : En cours de redémarrage..."
            )
            
            await channel.send(message)
            self.logger.info("Message de progression de redémarrage envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de progression: {e}")

    async def send_restart_success(self, channel, elapsed_time: int) -> None:
        """
        Envoie un message de succès du redémarrage
        
        Args:
            channel: Canal Discord
            elapsed_time: Temps de redémarrage en secondes
        """
        try:
            message = (
                f"✅ **Serveur Minecraft redémarré avec succès !**\n"
                f"⏱️ Temps de redémarrage : **{elapsed_time} secondes**\n"
                f"🎮 Le serveur est maintenant disponible pour les connexions."
            )
            
            await channel.send(message)
            self.logger.info(f"Message de succès de redémarrage envoyé ({elapsed_time}s)")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message de succès: {e}")

    async def send_restart_failed(self, channel) -> None:
        """
        Envoie un message d'échec du redémarrage
        
        Args:
            channel: Canal Discord
        """
        try:
            message = (
                f"❌ **Échec du redémarrage du serveur Minecraft**\n"
                f"🔧 Le serveur n'a pas pu être redémarré dans les délais impartis.\n"
                f"📞 Un administrateur a été notifié automatiquement."
            )
            
            await channel.send(message)
            self.logger.info("Message d'échec de redémarrage envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'échec: {e}")

    async def send_help_message(self, channel, help_text: str = None) -> None:
        """
        Envoie un message d'aide pour les commandes
        
        Args:
            channel: Canal Discord
            help_text: Texte d'aide personnalisé (optionnel)
        """
        try:
            if help_text:
                message = help_text
            else:
                # Message d'aide par défaut selon le cahier des charges
                message = (
                    f"🆘 **Aide - Commandes disponibles**\n\n"
                    f"🎮 **Redémarrer Minecraft :** Mentionnez-moi avec une phrase comme :\n"
                    f"   • \"@CubeGuardian redémarrer le serveur minecraft\"\n"
                    f"   • \"@CubeGuardian restart minecraft\"\n"
                    f"   • \"@CubeGuardian reboot serveur\"\n\n"
                    f"📝 **Variantes acceptées :**\n"
                    f"   • redémarrer, restart, reboot, relancer\n"
                    f"   • serveur, server, minecraft, mc\n\n"
                    f"⚠️ **Restrictions :**\n"
                    f"   • Seuls les joueurs autorisés peuvent utiliser les commandes\n"
                    f"   • Cooldown de 10 minutes entre les commandes\n"
                    f"   • Confirmation requise avant exécution\n\n"
                    f"💡 **Astuce :** Le bot tolère les fautes d'orthographe !"
                )
            
            await channel.send(message)
            self.logger.info("Message d'aide envoyé")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi du message d'aide: {e}")

    def __str__(self) -> str:
        """Représentation string du gestionnaire de messages"""
        text_name = self.text_channel.name if self.text_channel else "Non défini"
        voice_name = self.voice_channel.name if self.voice_channel else "Non défini"
        admin_name = self.admin_user.name if self.admin_user else "Non défini"
        
        return f"MessageManager(text={text_name}, voice={voice_name}, admin={admin_name})"
