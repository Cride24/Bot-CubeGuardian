"""
Gestionnaire de configuration pour Bot CubeGuardian
Charge et valide tous les fichiers de configuration YAML
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

class ConfigManager:
    """Gestionnaire centralisé de la configuration du bot"""
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialise le gestionnaire de configuration
        
        Args:
            config_dir: Répertoire contenant les fichiers de configuration
        """
        self.config_dir = Path(config_dir)
        self.config = {}
        self.logger = logging.getLogger('CubeGuardian.ConfigManager')
        
        # Chargement des variables d'environnement
        load_dotenv()
        
        # Chargement de la configuration
        self.load_all_configs()
    
    def load_all_configs(self) -> None:
        """Charge tous les fichiers de configuration"""
        config_files = {
            'bot': 'bot.yaml',
            'servers': 'servers.yaml', 
            'discord': 'discord.yaml',
            'messages': 'messages.yaml',
            'users': 'users.yaml'
        }
        
        for config_name, filename in config_files.items():
            try:
                config_path = self.config_dir / filename
                if config_path.exists():
                    self.config[config_name] = self.load_yaml_config(config_path)
                    self.logger.info(f"Configuration {config_name} chargée depuis {filename}")
                else:
                    self.logger.warning(f"Fichier de configuration manquant: {filename}")
                    self.config[config_name] = {}
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement de {filename}: {e}")
                self.config[config_name] = {}
    
    def load_yaml_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Charge un fichier de configuration YAML
        
        Args:
            config_path: Chemin vers le fichier YAML
            
        Returns:
            Dictionnaire contenant la configuration
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # Remplacement des variables d'environnement
            config = self._replace_env_variables(config)
            
            return config if config else {}
            
        except yaml.YAMLError as e:
            self.logger.error(f"Erreur YAML dans {config_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture de {config_path}: {e}")
            raise
    
    def _replace_env_variables(self, config: Any) -> Any:
        """
        Remplace les variables d'environnement dans la configuration
        
        Args:
            config: Configuration à traiter
            
        Returns:
            Configuration avec variables remplacées
        """
        if isinstance(config, dict):
            return {key: self._replace_env_variables(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_variables(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            # Format: ${VARIABLE_NAME}
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        else:
            return config
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration
        
        Args:
            key: Clé de configuration (format: 'section.key.subkey')
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration ou valeur par défaut
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de la config '{key}': {e}")
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """
        Définit une valeur de configuration
        
        Args:
            key: Clé de configuration (format: 'section.key.subkey')
            value: Valeur à définir
            
        Returns:
            True si la valeur a été définie avec succès
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # Naviguer jusqu'au niveau parent
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Définir la valeur finale
            config[keys[-1]] = value
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la définition de la config '{key}': {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        Valide la configuration complète
        
        Returns:
            True si la configuration est valide
        """
        required_configs = {
            'bot.bot.name': 'Nom du bot',
            'bot.bot.version': 'Version du bot',
            'discord.discord.token': 'Token Discord',
            'discord.discord.channels.voice_channel': 'Salon vocal',
            'discord.discord.channels.text_channel': 'Salon textuel',
            'servers.servers.proxmox.ipv4': 'IP du serveur Proxmox',
            'servers.servers.proxmox.mac_address': 'Adresse MAC Proxmox',
            'servers.servers.minecraft.ipv4': 'IP du serveur Minecraft',
            'servers.servers.minecraft.port': 'Port Minecraft'
        }
        
        missing_configs = []
        
        for config_key, description in required_configs.items():
            if not self.get_config(config_key):
                missing_configs.append(f"{config_key} ({description})")
        
        if missing_configs:
            self.logger.error(f"Configuration invalide. Éléments manquants: {', '.join(missing_configs)}")
            return False
        
        # Validation spécifique du token Discord
        discord_token = self.get_config('discord.discord.token')
        if not discord_token or discord_token == '${DISCORD_BOT_TOKEN}':
            self.logger.error("Token Discord non configuré dans les variables d'environnement")
            return False
        
        self.logger.info("Configuration validée avec succès")
        return True
    
    def reload_config(self) -> bool:
        """
        Recharge la configuration depuis les fichiers
        
        Returns:
            True si le rechargement a réussi
        """
        try:
            self.load_all_configs()
            return self.validate_config()
        except Exception as e:
            self.logger.error(f"Erreur lors du rechargement de la configuration: {e}")
            return False
    
    def get_discord_intents(self) -> Dict[str, bool]:
        """
        Récupère les intents Discord configurés
        
        Returns:
            Dictionnaire des intents Discord
        """
        intents_config = self.get_config('discord.intents', [])
        
        # Intents par défaut
        intents = {
            'voice_states': False,
            'members': False,
            'guilds': False,
            'messages': False,
            'message_content': False
        }
        
        # Activation des intents configurés
        for intent in intents_config:
            if intent in intents:
                intents[intent] = True
        
        return intents
    
    def get_authorized_users(self) -> list:
        """
        Récupère la liste des utilisateurs autorisés depuis les groupes
        
        Returns:
            Liste des utilisateurs autorisés (admins + players)
        """
        groups = self.get_config('users.groups', {})
        admins = groups.get('admins', [])
        players = groups.get('players', [])
        # Combiner les deux groupes et supprimer les doublons
        all_users = list(set(admins + players))
        return all_users
    
    def is_user_authorized(self, user_id: int) -> bool:
        """
        Vérifie si un utilisateur est autorisé
        
        Args:
            user_id: ID Discord de l'utilisateur
            
        Returns:
            True si l'utilisateur est autorisé
        """
        authorized_users = self.get_authorized_users()
        # Format simple : liste d'IDs en string
        return str(user_id) in authorized_users
    
    def get_user_permissions(self, user_id: int) -> list:
        """
        Récupère les permissions d'un utilisateur basées sur son groupe
        
        Args:
            user_id: ID Discord de l'utilisateur
            
        Returns:
            Liste des permissions de l'utilisateur
        """
        groups = self.get_config('users.groups', {})
        admins = groups.get('admins', [])
        players = groups.get('players', [])
        
        user_id_str = str(user_id)
        
        # Si l'utilisateur est admin, il a toutes les permissions
        if user_id_str in admins:
            return ["start_server", "stop_server", "admin_commands"]
        
        # Si l'utilisateur est player, il a les permissions de base
        if user_id_str in players:
            return ["start_server", "stop_server"]
        
        return []
    
    def get_message(self, message_key: str, **kwargs) -> str:
        """
        Récupère un message formaté
        
        Args:
            message_key: Clé du message (format: 'section.subsection')
            **kwargs: Variables pour le formatage
            
        Returns:
            Message formaté
        """
        message = self.get_config(f'messages.messages.{message_key}', f'Message manquant: {message_key}')
        
        if isinstance(message, str) and kwargs:
            try:
                return message.format(**kwargs)
            except KeyError as e:
                self.logger.warning(f"Variable manquante pour le message {message_key}: {e}")
                return message
        
        return message
    
    def get_script_path(self, script_name: str) -> str:
        """
        Récupère le chemin d'un script PowerShell
        
        Args:
            script_name: Nom du script (wakeup, shutdown, check_proxmox, check_minecraft)
            
        Returns:
            Chemin vers le script
        """
        script_mapping = {
            'wakeup': 'scripts.wakeup_script',
            'shutdown': 'scripts.shutdown_script',
            'check_proxmox': 'scripts.check_proxmox_script',
            'check_minecraft': 'scripts.check_minecraft_script'
        }
        
        if script_name in script_mapping:
            return self.get_config(script_mapping[script_name], f'./scripts/{script_name}-pve-bot.ps1')
        
        raise ValueError(f"Script inconnu: {script_name}")
    
    def get_timer(self, timer_name: str) -> int:
        """
        Récupère la valeur d'un timer
        
        Args:
            timer_name: Nom du timer
            
        Returns:
            Valeur du timer en secondes
        """
        return self.get_config(f'timers.{timer_name}', 60)
    
    def get_server_config(self, server_name: str) -> Dict[str, Any]:
        """
        Récupère la configuration d'un serveur
        
        Args:
            server_name: Nom du serveur (proxmox, minecraft)
            
        Returns:
            Configuration du serveur
        """
        return self.get_config(f'servers.servers.{server_name}', {})
    
    def __str__(self) -> str:
        """Représentation string de la configuration"""
        return f"ConfigManager(config_dir={self.config_dir}, sections={list(self.config.keys())})"
