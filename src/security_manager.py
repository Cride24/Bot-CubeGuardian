#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Manager - Système de sécurité avancé pour Bot CubeGuardian
Gestion des cooldowns, rate limiting et validation des commandes
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum

class SecurityLevel(Enum):
    """Niveaux de sécurité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class UserCooldown:
    """Information de cooldown pour un utilisateur"""
    user_id: int
    last_command_time: float
    command_count: int
    daily_commands: int
    warning_count: int
    banned_until: Optional[float] = None

@dataclass
class SecurityEvent:
    """Événement de sécurité"""
    user_id: int
    event_type: str
    timestamp: float
    details: Dict
    level: SecurityLevel

class SecurityManager:
    """
    Gestionnaire de sécurité pour les commandes interactives
    Cooldowns, rate limiting, détection d'abus
    """
    
    def __init__(self, config_manager, log_manager):
        """
        Initialise le gestionnaire de sécurité
        
        Args:
            config_manager: Gestionnaire de configuration
            log_manager: Gestionnaire de logs
        """
        self.config_manager = config_manager
        self.log_manager = log_manager
        self.logger = logging.getLogger('CubeGuardian.SecurityManager')
        
        # Configuration sécurité
        self.cooldown_duration = 600  # 10 minutes en secondes
        self.max_commands_per_hour = 6  # Maximum 6 commandes par heure
        self.max_commands_per_day = 20  # Maximum 20 commandes par jour
        self.spam_threshold = 3  # 3 tentatives en spam = warning
        self.ban_duration = 3600  # 1 heure de ban temporaire
        
        # Stockage des données utilisateur
        self.user_cooldowns: Dict[int, UserCooldown] = {}
        self.user_attempts: Dict[int, deque] = defaultdict(lambda: deque(maxlen=10))
        self.security_events: List[SecurityEvent] = []
        self.banned_users: Dict[int, float] = {}
        
        # Rate limiting par endpoint
        self.rate_limits = {
            'restart_command': {'limit': 1, 'window': 600},  # 1 redémarrage / 10min
            'help_command': {'limit': 5, 'window': 60},      # 5 aides / 1min
            'status_check': {'limit': 10, 'window': 60}      # 10 statuts / 1min
        }
        self.rate_limit_buckets: Dict[str, Dict[int, deque]] = {
            endpoint: defaultdict(lambda: deque(maxlen=limit['limit']))
            for endpoint, limit in self.rate_limits.items()
        }
        
        self.logger.info("SecurityManager initialisé")

    def check_user_cooldown(self, user_id: int) -> bool:
        """
        Vérifie si l'utilisateur peut exécuter une commande (cooldown 10min)
        
        Args:
            user_id: ID de l'utilisateur Discord
            
        Returns:
            True si l'utilisateur peut exécuter une commande, False sinon
        """
        try:
            current_time = time.time()
            
            # Vérifier si l'utilisateur est temporairement banni
            if self._is_user_banned(user_id, current_time):
                self.logger.warning(f"Utilisateur {user_id} temporairement banni")
                return False
            
            # Récupérer ou créer le cooldown utilisateur
            if user_id not in self.user_cooldowns:
                self.user_cooldowns[user_id] = UserCooldown(
                    user_id=user_id,
                    last_command_time=0.0,
                    command_count=0,
                    daily_commands=0,
                    warning_count=0
                )
            
            user_cooldown = self.user_cooldowns[user_id]
            
            # Vérifier le cooldown principal (10 minutes)
            time_since_last = current_time - user_cooldown.last_command_time
            if time_since_last < self.cooldown_duration:
                remaining = self.cooldown_duration - time_since_last
                self.logger.info(f"Cooldown actif pour {user_id} - {remaining:.0f}s restantes")
                
                # Enregistrer tentative pendant cooldown
                self._record_security_event(
                    user_id, "cooldown_violation", current_time,
                    {"remaining_seconds": remaining}, SecurityLevel.LOW
                )
                return False
            
            # Vérifier les limites quotidiennes
            if not self._check_daily_limits(user_id, current_time):
                return False
            
            # Vérifier le rate limiting
            if not self._check_rate_limit(user_id, 'restart_command', current_time):
                return False
            
            self.logger.info(f"Cooldown OK pour utilisateur {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification du cooldown: {e}")
            return False

    def update_user_cooldown(self, user_id: int) -> None:
        """
        Met à jour le cooldown de l'utilisateur après une commande réussie
        
        Args:
            user_id: ID de l'utilisateur Discord
        """
        try:
            current_time = time.time()
            
            # Créer ou mettre à jour le cooldown
            if user_id not in self.user_cooldowns:
                self.user_cooldowns[user_id] = UserCooldown(
                    user_id=user_id,
                    last_command_time=current_time,
                    command_count=1,
                    daily_commands=1,
                    warning_count=0
                )
            else:
                user_cooldown = self.user_cooldowns[user_id]
                user_cooldown.last_command_time = current_time
                user_cooldown.command_count += 1
                
                # Réinitialiser les commandes quotidiennes si nouveau jour
                if self._is_new_day(user_cooldown.last_command_time, current_time):
                    user_cooldown.daily_commands = 1
                else:
                    user_cooldown.daily_commands += 1
            
            # Enregistrer l'événement de sécurité
            self._record_security_event(
                user_id, "command_executed", current_time,
                {"command_type": "restart_minecraft"}, SecurityLevel.LOW
            )
            
            # Mettre à jour le rate limiting
            self._update_rate_limit(user_id, 'restart_command', current_time)
            
            self.logger.info(f"Cooldown mis à jour pour utilisateur {user_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du cooldown: {e}")

    def get_user_cooldown_remaining(self, user_id: int) -> int:
        """
        Récupère le temps restant du cooldown en minutes
        
        Args:
            user_id: ID de l'utilisateur Discord
            
        Returns:
            Nombre de minutes restantes (0 si pas de cooldown)
        """
        try:
            if user_id not in self.user_cooldowns:
                return 0
            
            current_time = time.time()
            user_cooldown = self.user_cooldowns[user_id]
            
            time_since_last = current_time - user_cooldown.last_command_time
            remaining_seconds = max(0, self.cooldown_duration - time_since_last)
            remaining_minutes = int(remaining_seconds / 60) + (1 if remaining_seconds % 60 > 0 else 0)
            
            return remaining_minutes
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du cooldown restant: {e}")
            return 0

    def check_spam_detection(self, user_id: int) -> Tuple[bool, str]:
        """
        Détecte les tentatives de spam et applique des sanctions
        
        Args:
            user_id: ID de l'utilisateur Discord
            
        Returns:
            Tuple (is_spam, reason)
        """
        try:
            current_time = time.time()
            
            # Ajouter la tentative actuelle
            self.user_attempts[user_id].append(current_time)
            
            # Compter les tentatives dans la dernière minute
            recent_attempts = [
                t for t in self.user_attempts[user_id]
                if current_time - t < 60
            ]
            
            if len(recent_attempts) >= self.spam_threshold:
                # Spam détecté !
                self._handle_spam_detection(user_id, current_time, len(recent_attempts))
                return True, f"Spam détecté: {len(recent_attempts)} tentatives en 1 minute"
            
            return False, ""
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection de spam: {e}")
            return False, ""

    def get_user_security_status(self, user_id: int) -> Dict:
        """
        Récupère le statut de sécurité complet d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur Discord
            
        Returns:
            Dictionnaire avec le statut de sécurité
        """
        try:
            current_time = time.time()
            
            if user_id not in self.user_cooldowns:
                return {
                    'cooldown_active': False,
                    'minutes_remaining': 0,
                    'commands_today': 0,
                    'warning_count': 0,
                    'is_banned': False,
                    'security_level': SecurityLevel.LOW.value
                }
            
            user_cooldown = self.user_cooldowns[user_id]
            
            return {
                'cooldown_active': not self.check_user_cooldown(user_id),
                'minutes_remaining': self.get_user_cooldown_remaining(user_id),
                'commands_today': user_cooldown.daily_commands,
                'warning_count': user_cooldown.warning_count,
                'is_banned': self._is_user_banned(user_id, current_time),
                'security_level': self._get_user_security_level(user_id).value,
                'last_command': datetime.fromtimestamp(user_cooldown.last_command_time).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du statut: {e}")
            return {'error': str(e)}

    def _is_user_banned(self, user_id: int, current_time: float) -> bool:
        """Vérifie si l'utilisateur est temporairement banni"""
        if user_id in self.banned_users:
            ban_until = self.banned_users[user_id]
            if current_time < ban_until:
                return True
            else:
                # Ban expiré, nettoyer
                del self.banned_users[user_id]
        return False

    def _check_daily_limits(self, user_id: int, current_time: float) -> bool:
        """Vérifie les limites quotidiennes"""
        if user_id in self.user_cooldowns:
            user_cooldown = self.user_cooldowns[user_id]
            
            # Réinitialiser si nouveau jour
            if self._is_new_day(user_cooldown.last_command_time, current_time):
                user_cooldown.daily_commands = 0
            
            if user_cooldown.daily_commands >= self.max_commands_per_day:
                self._record_security_event(
                    user_id, "daily_limit_exceeded", current_time,
                    {"daily_commands": user_cooldown.daily_commands}, SecurityLevel.MEDIUM
                )
                return False
        return True

    def _check_rate_limit(self, user_id: int, endpoint: str, current_time: float) -> bool:
        """Vérifie le rate limiting pour un endpoint"""
        if endpoint not in self.rate_limits:
            return True
        
        limit_config = self.rate_limits[endpoint]
        user_bucket = self.rate_limit_buckets[endpoint][user_id]
        
        # Nettoyer les anciennes entrées
        while user_bucket and current_time - user_bucket[0] > limit_config['window']:
            user_bucket.popleft()
        
        if len(user_bucket) >= limit_config['limit']:
            self._record_security_event(
                user_id, "rate_limit_exceeded", current_time,
                {"endpoint": endpoint, "attempts": len(user_bucket)}, SecurityLevel.MEDIUM
            )
            return False
        
        return True

    def _update_rate_limit(self, user_id: int, endpoint: str, current_time: float):
        """Met à jour le rate limiting après une commande"""
        if endpoint in self.rate_limit_buckets:
            self.rate_limit_buckets[endpoint][user_id].append(current_time)

    def _handle_spam_detection(self, user_id: int, current_time: float, attempt_count: int):
        """Gère la détection de spam et applique des sanctions"""
        if user_id in self.user_cooldowns:
            self.user_cooldowns[user_id].warning_count += 1
            warning_count = self.user_cooldowns[user_id].warning_count
        else:
            warning_count = 1
        
        # Escalade des sanctions
        if warning_count >= 3:
            # Ban temporaire après 3 warnings
            self.banned_users[user_id] = current_time + self.ban_duration
            
            self._record_security_event(
                user_id, "temporary_ban", current_time,
                {"reason": "spam_detection", "ban_duration": self.ban_duration,
                 "attempt_count": attempt_count}, SecurityLevel.HIGH
            )
        else:
            self._record_security_event(
                user_id, "spam_warning", current_time,
                {"warning_count": warning_count, "attempt_count": attempt_count}, 
                SecurityLevel.MEDIUM
            )

    def _record_security_event(self, user_id: int, event_type: str, timestamp: float, 
                              details: Dict, level: SecurityLevel):
        """Enregistre un événement de sécurité"""
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            timestamp=timestamp,
            details=details,
            level=level
        )
        
        self.security_events.append(event)
        
        # Garder seulement les 1000 derniers événements
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        # Logger selon le niveau
        log_message = f"Security Event - User {user_id}: {event_type} - {details}"
        if level == SecurityLevel.LOW:
            self.logger.info(log_message)
        elif level == SecurityLevel.MEDIUM:
            self.logger.warning(log_message)
        elif level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            self.logger.error(log_message)

    def _get_user_security_level(self, user_id: int) -> SecurityLevel:
        """Détermine le niveau de sécurité d'un utilisateur"""
        if user_id not in self.user_cooldowns:
            return SecurityLevel.LOW
        
        user_cooldown = self.user_cooldowns[user_id]
        
        if user_cooldown.warning_count >= 3:
            return SecurityLevel.HIGH
        elif user_cooldown.warning_count >= 1:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW

    def _is_new_day(self, last_time: float, current_time: float) -> bool:
        """Vérifie si c'est un nouveau jour depuis la dernière commande"""
        last_date = datetime.fromtimestamp(last_time).date()
        current_date = datetime.fromtimestamp(current_time).date()
        return current_date > last_date

    def get_security_statistics(self) -> Dict:
        """Récupère les statistiques de sécurité"""
        try:
            current_time = time.time()
            
            # Compter les événements par type
            event_counts = defaultdict(int)
            recent_events = 0
            
            for event in self.security_events:
                event_counts[event.event_type] += 1
                if current_time - event.timestamp < 3600:  # Dernière heure
                    recent_events += 1
            
            return {
                'total_users': len(self.user_cooldowns),
                'banned_users': len(self.banned_users),
                'total_events': len(self.security_events),
                'recent_events_1h': recent_events,
                'event_counts': dict(event_counts),
                'active_cooldowns': len([
                    u for u in self.user_cooldowns.values()
                    if current_time - u.last_command_time < self.cooldown_duration
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {'error': str(e)}

    def cleanup_old_data(self) -> None:
        """Nettoie les données anciennes pour éviter la surconsommation mémoire"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (24 * 3600)  # 24 heures
            
            # Nettoyer les événements anciens
            self.security_events = [
                event for event in self.security_events
                if event.timestamp > cutoff_time
            ]
            
            # Nettoyer les tentatives anciennes
            for user_id in list(self.user_attempts.keys()):
                recent_attempts = deque([
                    t for t in self.user_attempts[user_id]
                    if current_time - t < 3600  # Garder 1 heure
                ], maxlen=10)
                
                if recent_attempts:
                    self.user_attempts[user_id] = recent_attempts
                else:
                    del self.user_attempts[user_id]
            
            # Nettoyer les bans expirés
            expired_bans = [
                user_id for user_id, ban_until in self.banned_users.items()
                if current_time >= ban_until
            ]
            for user_id in expired_bans:
                del self.banned_users[user_id]
            
            self.logger.info("Nettoyage des données de sécurité effectué")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage: {e}")
