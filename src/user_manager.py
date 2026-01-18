"""
Gestionnaire d'utilisateurs pour Bot CubeGuardian
Gestion des utilisateurs autorisés et des permissions
"""

import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AuthorizedUser:
    """Représentation d'un utilisateur autorisé"""
    user_id: int
    username: str
    display_name: str
    permissions: List[str]
    added_date: datetime
    last_seen: Optional[datetime] = None

class UserManager:
    """Gestionnaire des utilisateurs autorisés"""
    
    def __init__(self, config_manager, log_manager):
        """
        Initialise le gestionnaire d'utilisateurs
        
        Args:
            config_manager: Gestionnaire de configuration
            log_manager: Gestionnaire de logs
        """
        self.config_manager = config_manager
        self.log_manager = log_manager
        self.logger = logging.getLogger('CubeGuardian.UserManager')
        
        # Chargement des utilisateurs autorisés
        self.authorized_users = self._load_authorized_users()
        self.groups = self._load_groups()
        
        # Utilisateurs actuellement présents dans le salon vocal
        self.users_present = set()
        
        self.logger.info(f"UserManager initialisé avec {len(self.authorized_users)} utilisateurs autorisés")
    
    def _load_authorized_users(self) -> Dict[int, AuthorizedUser]:
        """
        Charge les utilisateurs autorisés depuis la configuration (format groups)
        
        Returns:
            Dictionnaire des utilisateurs autorisés
        """
        users_config = self.config_manager.get_authorized_users()  # Liste d'IDs en string
        authorized_users = {}
        
        for user_id_str in users_config:
            try:
                user_id = int(user_id_str)
                permissions = self.config_manager.get_user_permissions(user_id)
                
                user = AuthorizedUser(
                    user_id=user_id,
                    username=f"User_{user_id}",  # Nom par défaut
                    display_name=f"Utilisateur {user_id}",  # Nom d'affichage par défaut
                    permissions=permissions,
                    added_date=datetime.now()
                )
                authorized_users[user_id] = user
                
            except (ValueError, KeyError) as e:
                self.logger.error(f"Erreur lors du chargement de l'utilisateur {user_id_str}: {e}")
        
        return authorized_users
    
    def _load_groups(self) -> Dict[str, List[int]]:
        """
        Charge les groupes d'utilisateurs depuis la configuration
        
        Returns:
            Dictionnaire des groupes
        """
        groups_config = self.config_manager.get_config('groups', {})
        groups = {}
        
        for group_name, user_ids in groups_config.items():
            groups[group_name] = [int(user_id) for user_id in user_ids]
        
        return groups
    
    def is_authorized(self, user_id: int) -> bool:
        """
        Vérifie si un utilisateur est autorisé
        
        Args:
            user_id: ID Discord de l'utilisateur
            
        Returns:
            True si l'utilisateur est autorisé
        """
        return user_id in self.authorized_users
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Récupère les permissions d'un utilisateur
        
        Args:
            user_id: ID Discord de l'utilisateur
            
        Returns:
            Liste des permissions de l'utilisateur
        """
        if user_id in self.authorized_users:
            return self.authorized_users[user_id].permissions
        return []
    
    def has_permission(self, user_id: int, permission: str) -> bool:
        """
        Vérifie si un utilisateur a une permission spécifique
        
        Args:
            user_id: ID Discord de l'utilisateur
            permission: Permission à vérifier
            
        Returns:
            True si l'utilisateur a la permission
        """
        if not self.is_authorized(user_id):
            return False
        
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions
    
    def add_authorized_user(self, user_id: int, username: str, display_name: str, permissions: List[str]) -> bool:
        """
        Ajoute un utilisateur autorisé
        
        Args:
            user_id: ID Discord de l'utilisateur
            username: Nom d'utilisateur Discord
            display_name: Nom d'affichage
            permissions: Liste des permissions
            
        Returns:
            True si l'utilisateur a été ajouté avec succès
        """
        try:
            if user_id in self.authorized_users:
                self.logger.warning(f"Utilisateur {user_id} déjà autorisé")
                return False
            
            user = AuthorizedUser(
                user_id=user_id,
                username=username,
                display_name=display_name,
                permissions=permissions,
                added_date=datetime.now()
            )
            
            self.authorized_users[user_id] = user
            self.logger.info(f"Utilisateur {username} ({user_id}) ajouté avec les permissions: {permissions}")
            self.log_manager.log_info(f"Utilisateur autorisé ajouté: {username} ({user_id})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de l'utilisateur {user_id}: {e}")
            return False
    
    def remove_authorized_user(self, user_id: int) -> bool:
        """
        Retire un utilisateur autorisé
        
        Args:
            user_id: ID Discord de l'utilisateur
            
        Returns:
            True si l'utilisateur a été retiré avec succès
        """
        try:
            if user_id not in self.authorized_users:
                self.logger.warning(f"Utilisateur {user_id} non trouvé dans les utilisateurs autorisés")
                return False
            
            user = self.authorized_users[user_id]
            del self.authorized_users[user_id]
            
            # Retirer de la liste des utilisateurs présents si nécessaire
            self.users_present.discard(user_id)
            
            self.logger.info(f"Utilisateur {user.username} ({user_id}) retiré des utilisateurs autorisés")
            self.log_manager.log_info(f"Utilisateur autorisé retiré: {user.username} ({user_id})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression de l'utilisateur {user_id}: {e}")
            return False
    
    def update_user_permissions(self, user_id: int, permissions: List[str]) -> bool:
        """
        Met à jour les permissions d'un utilisateur
        
        Args:
            user_id: ID Discord de l'utilisateur
            permissions: Nouvelles permissions
            
        Returns:
            True si les permissions ont été mises à jour avec succès
        """
        try:
            if user_id not in self.authorized_users:
                self.logger.warning(f"Utilisateur {user_id} non trouvé")
                return False
            
            old_permissions = self.authorized_users[user_id].permissions
            self.authorized_users[user_id].permissions = permissions
            
            self.logger.info(f"Permissions mises à jour pour l'utilisateur {user_id}: {old_permissions} -> {permissions}")
            self.log_manager.log_info(f"Permissions mises à jour pour l'utilisateur {user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des permissions pour l'utilisateur {user_id}: {e}")
            return False
    
    def get_authorized_users_present(self, voice_channel) -> List[AuthorizedUser]:
        """
        Récupère la liste des utilisateurs autorisés présents dans un salon vocal
        
        Args:
            voice_channel: Salon vocal Discord
            
        Returns:
            Liste des utilisateurs autorisés présents
        """
        if not voice_channel:
            return []
        
        present_users = []
        
        for member in voice_channel.members:
            if self.is_authorized(member.id):
                user = self.authorized_users[member.id]
                # Mettre à jour la dernière fois vue
                user.last_seen = datetime.now()
                present_users.append(user)
        
        return present_users
    
    def get_authorized_users_count(self, voice_channel) -> int:
        """
        Compte le nombre d'utilisateurs autorisés présents dans un salon vocal
        
        Args:
            voice_channel: Salon vocal Discord
            
        Returns:
            Nombre d'utilisateurs autorisés présents
        """
        return len(self.get_authorized_users_present(voice_channel))
    
    def update_user_presence(self, user_id: int, is_present: bool) -> None:
        """
        Met à jour la présence d'un utilisateur
        
        Args:
            user_id: ID Discord de l'utilisateur
            is_present: True si l'utilisateur est présent
        """
        if is_present:
            self.users_present.add(user_id)
            if user_id in self.authorized_users:
                self.authorized_users[user_id].last_seen = datetime.now()
        else:
            self.users_present.discard(user_id)
    
    def get_users_in_group(self, group_name: str) -> List[AuthorizedUser]:
        """
        Récupère les utilisateurs d'un groupe
        
        Args:
            group_name: Nom du groupe
            
        Returns:
            Liste des utilisateurs du groupe
        """
        if group_name not in self.groups:
            return []
        
        group_users = []
        for user_id in self.groups[group_name]:
            if user_id in self.authorized_users:
                group_users.append(self.authorized_users[user_id])
        
        return group_users
    
    def is_user_in_group(self, user_id: int, group_name: str) -> bool:
        """
        Vérifie si un utilisateur appartient à un groupe
        
        Args:
            user_id: ID Discord de l'utilisateur
            group_name: Nom du groupe
            
        Returns:
            True si l'utilisateur appartient au groupe
        """
        if group_name not in self.groups:
            return False
        
        return user_id in self.groups[group_name]
    
    def get_user_info(self, user_id: int) -> Optional[AuthorizedUser]:
        """
        Récupère les informations d'un utilisateur
        
        Args:
            user_id: ID Discord de l'utilisateur
            
        Returns:
            Informations de l'utilisateur ou None
        """
        return self.authorized_users.get(user_id)
    
    def get_all_authorized_users(self) -> List[AuthorizedUser]:
        """
        Récupère tous les utilisateurs autorisés
        
        Returns:
            Liste de tous les utilisateurs autorisés
        """
        return list(self.authorized_users.values())
    
    def get_users_with_permission(self, permission: str) -> List[AuthorizedUser]:
        """
        Récupère les utilisateurs ayant une permission spécifique
        
        Args:
            permission: Permission à rechercher
            
        Returns:
            Liste des utilisateurs ayant la permission
        """
        users_with_permission = []
        
        for user in self.authorized_users.values():
            if permission in user.permissions:
                users_with_permission.append(user)
        
        return users_with_permission
    
    def get_admin_users(self) -> List[AuthorizedUser]:
        """
        Récupère les utilisateurs administrateurs
        
        Returns:
            Liste des utilisateurs administrateurs
        """
        return self.get_users_with_permission('admin_commands')
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des utilisateurs
        
        Returns:
            Dictionnaire avec les statistiques
        """
        total_users = len(self.authorized_users)
        present_users = len(self.users_present)
        
        # Compter les permissions
        permission_counts = {}
        for user in self.authorized_users.values():
            for permission in user.permissions:
                permission_counts[permission] = permission_counts.get(permission, 0) + 1
        
        # Compter les groupes
        group_counts = {}
        for group_name, user_ids in self.groups.items():
            group_counts[group_name] = len(user_ids)
        
        return {
            'total_authorized_users': total_users,
            'present_users': present_users,
            'permission_counts': permission_counts,
            'group_counts': group_counts,
            'groups': list(self.groups.keys())
        }
    
    def validate_user_permissions(self, user_id: int, required_permissions: List[str]) -> bool:
        """
        Valide qu'un utilisateur a toutes les permissions requises
        
        Args:
            user_id: ID Discord de l'utilisateur
            required_permissions: Permissions requises
            
        Returns:
            True si l'utilisateur a toutes les permissions
        """
        if not self.is_authorized(user_id):
            return False
        
        user_permissions = self.get_user_permissions(user_id)
        return all(permission in user_permissions for permission in required_permissions)
    
    def __str__(self) -> str:
        """Représentation string du gestionnaire d'utilisateurs"""
        return f"UserManager(authorized_users={len(self.authorized_users)}, present_users={len(self.users_present)})"
