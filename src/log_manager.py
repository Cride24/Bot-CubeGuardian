"""
Gestionnaire de logs pour Bot CubeGuardian
Gestion centralisée des logs avec rotation automatique par nombre de lignes
"""

import logging
import logging.handlers
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class LogManager:
    """Gestionnaire de logs centralisé avec rotation par lignes"""
    
    def __init__(self, config_manager):
        """
        Initialise le gestionnaire de logs
        
        Args:
            config_manager: Instance de ConfigManager
        """
        self.config_manager = config_manager
        self.logger = None
        
        # Récupération de la configuration des logs
        logging_config = config_manager.get_config('bot', {}).get('logging', {})
        
        self.log_file_path = Path(logging_config.get('file_path', './logs/cubeguardian.log'))
        self.max_lines = logging_config.get('max_lines', 200)
        self.rotation_enabled = logging_config.get('rotation_enabled', True)
        self.keep_oldest = logging_config.get('keep_oldest', False)
        
        # Création du répertoire de logs
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuration du logger
        self.setup_logging()
    
    def setup_logging(self) -> logging.Logger:
        """
        Configure le système de logs
        
        Returns:
            Logger configuré
        """
        # Configuration du logger principal
        self.logger = logging.getLogger('CubeGuardian')
        
        # Récupération de la configuration des logs
        logging_config = self.config_manager.get_config('bot', {}).get('logging', {})
        
        # Récupération du niveau de log depuis la configuration
        bot_config = self.config_manager.get_config('bot', {})
        log_level = bot_config.get('log_level', 'INFO')
        self.logger.setLevel(getattr(logging, log_level))
        
        # Éviter les doublons de handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Handler fichier avec rotation par taille
        if logging_config.get('file_enabled', True):
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file_path,
                maxBytes=self._parse_size(logging_config.get('max_file_size', '10MB')),
                backupCount=logging_config.get('backup_count', 5),
                encoding='utf-8'
            )
            
            # Format des logs
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Premier log
        self.logger.info("Système de logs initialisé")
        
        return self.logger
    
    def _parse_size(self, size_str: str) -> int:
        """
        Convertit une taille en bytes
        
        Args:
            size_str: Taille sous forme de string (ex: "10MB", "1KB")
            
        Returns:
            Taille en bytes
        """
        size_str = size_str.upper().strip()
        
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def rotate_logs_by_lines(self) -> None:
        """Effectue la rotation des logs par nombre de lignes"""
        if not self.rotation_enabled or not self.log_file_path.exists():
            return
        
        try:
            # Lire toutes les lignes
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Vérifier si la limite est atteinte
            if len(lines) >= self.max_lines:
                # Calculer le nombre de lignes à conserver
                if self.keep_oldest:
                    # Garder les lignes les plus anciennes
                    lines_to_keep = lines[:self.max_lines//2]
                else:
                    # Garder les lignes les plus récentes
                    lines_to_keep = lines[-(self.max_lines//2):]
                
                # Réécrire le fichier avec les lignes conservées
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines_to_keep)
                
                # Log de la rotation
                self.logger.info(f"Rotation des logs effectuée: {len(lines)} -> {len(lines_to_keep)} lignes")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la rotation des logs: {e}")
    
    def log_with_rotation(self, level: str, message: str) -> None:
        """
        Log un message et vérifie la rotation
        
        Args:
            level: Niveau de log (debug, info, warning, error, critical)
            message: Message à logger
        """
        if self.logger:
            getattr(self.logger, level.lower())(message)
            self.rotate_logs_by_lines()
    
    def log_info(self, message: str) -> None:
        """Log un message d'information"""
        self.log_with_rotation('info', message)
    
    def log_warning(self, message: str) -> None:
        """Log un message d'avertissement"""
        self.log_with_rotation('warning', message)
    
    def log_error(self, message: str) -> None:
        """Log un message d'erreur"""
        self.log_with_rotation('error', message)
    
    def log_critical(self, message: str) -> None:
        """Log un message critique"""
        self.log_with_rotation('critical', message)
    
    def log_debug(self, message: str) -> None:
        """Log un message de debug"""
        self.log_with_rotation('debug', message)
    
    def log_voice_event(self, event_type: str, user: str, channel: str = None) -> None:
        """
        Log un événement vocal
        
        Args:
            event_type: Type d'événement (join, leave, move)
            user: Nom de l'utilisateur
            channel: Nom du salon (optionnel)
        """
        if channel:
            message = f"Événement vocal: {user} {event_type} {channel}"
        else:
            message = f"Événement vocal: {user} {event_type}"
        
        self.log_info(message)
    
    def log_server_event(self, event_type: str, server: str, details: str = None) -> None:
        """
        Log un événement serveur
        
        Args:
            event_type: Type d'événement (start, stop, check, error)
            server: Nom du serveur
            details: Détails supplémentaires (optionnel)
        """
        if details:
            message = f"Événement serveur {server}: {event_type} - {details}"
        else:
            message = f"Événement serveur {server}: {event_type}"
        
        if event_type in ['error', 'failed']:
            self.log_error(message)
        else:
            self.log_info(message)
    
    def log_powershell_script(self, script_name: str, success: bool, details: str = None) -> None:
        """
        Log l'exécution d'un script PowerShell
        
        Args:
            script_name: Nom du script
            success: Succès de l'exécution
            details: Détails supplémentaires (optionnel)
        """
        status = "SUCCÈS" if success else "ÉCHEC"
        message = f"Script PowerShell {script_name}: {status}"
        
        if details:
            message += f" - {details}"
        
        if success:
            self.log_info(message)
        else:
            self.log_error(message)
    
    def log_discord_event(self, event_type: str, details: str = None) -> None:
        """
        Log un événement Discord
        
        Args:
            event_type: Type d'événement (connect, disconnect, message, error)
            details: Détails supplémentaires (optionnel)
        """
        message = f"Événement Discord: {event_type}"
        
        if details:
            message += f" - {details}"
        
        if event_type in ['error', 'disconnect']:
            self.log_error(message)
        else:
            self.log_info(message)
    
    def log_bot_state_change(self, old_state: str, new_state: str, reason: str = None) -> None:
        """
        Log un changement d'état du bot
        
        Args:
            old_state: Ancien état
            new_state: Nouvel état
            reason: Raison du changement (optionnel)
        """
        message = f"Changement d'état: {old_state} -> {new_state}"
        
        if reason:
            message += f" (Raison: {reason})"
        
        self.log_info(message)
    
    def log_performance(self, operation: str, duration: float, details: str = None) -> None:
        """
        Log des métriques de performance
        
        Args:
            operation: Nom de l'opération
            duration: Durée en secondes
            details: Détails supplémentaires (optionnel)
        """
        message = f"Performance {operation}: {duration:.2f}s"
        
        if details:
            message += f" - {details}"
        
        self.log_info(message)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des logs
        
        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {
            'log_file_exists': self.log_file_path.exists(),
            'log_file_size': 0,
            'log_file_lines': 0,
            'rotation_enabled': self.rotation_enabled,
            'max_lines': self.max_lines
        }
        
        if self.log_file_path.exists():
            try:
                stats['log_file_size'] = self.log_file_path.stat().st_size
                
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    stats['log_file_lines'] = len(f.readlines())
                    
            except Exception as e:
                self.log_error(f"Erreur lors de la lecture des statistiques de logs: {e}")
        
        return stats
    
    def cleanup_old_logs(self, days_to_keep: int = 7) -> None:
        """
        Nettoie les anciens fichiers de logs
        
        Args:
            days_to_keep: Nombre de jours à conserver
        """
        if not self.log_file_path.parent.exists():
            return
        
        try:
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            for log_file in self.log_file_path.parent.glob('*.log*'):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.log_info(f"Ancien fichier de log supprimé: {log_file.name}")
                    
        except Exception as e:
            self.log_error(f"Erreur lors du nettoyage des anciens logs: {e}")
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire de logs"""
        return f"LogManager(file={self.log_file_path}, max_lines={self.max_lines}, rotation={self.rotation_enabled})"
