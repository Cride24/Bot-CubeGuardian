"""
Module de reconnaissance de commandes en langage naturel français
Reconnaissance des commandes de redémarrage Minecraft avec tolérance aux fautes
"""

import re
import unicodedata
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class CommandIntent(Enum):
    """Types de commandes détectées"""
    RESTART_MINECRAFT = "restart_minecraft"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class CommandResult:
    """Résultat de l'analyse d'une commande"""
    intent: CommandIntent
    confidence: float
    matched_keywords: List[str]
    original_text: str
    normalized_text: str


class CommandParser:
    """
    Analyseur de commandes en langage naturel français
    Supporte les fautes d'orthographe et les anglicismes
    """
    
    def __init__(self):
        """Initialise le parser avec les mots-clés de reconnaissance"""
        self.logger = logging.getLogger('CubeGuardian.CommandParser')
        
        # Mots-clés pour redémarrage - tolérance aux fautes d'orthographe
        self.restart_keywords = {
            # Français standard
            "redemarrer", "redémarrer", "redémarer", "redemarer", "redémarre", "redemarre",
            "relancer", "relencé", "relenser", "relance", "relence",
            "repartir", "repartie", "répartir", "repart", "repare",
            "rebouter", "rebooter", "rebooter",
            
            # Anglicismes courants
            "restart", "restar", "restard", "restat", "restarte",
            "reboot", "rebout", "rboot", "rebot",
            "reset", "rese", "resete",
            
            # Synonymes
            "arreter", "arrêter", "stop", "stopper", "arrête", "arret",
            "demarrer", "démarrer", "demarre", "demarer", "start", "starte"
        }
        
        # Mots-clés pour serveur/minecraft
        self.server_keywords = {
            "serveur", "server", "servere", "sever", "serv",
            "minecraft", "mine", "mc", "minecraf", "mincraft", "craft",
            "jeu", "game", "partie", "world", "monde"
        }
        
        # Mots-clés d'aide
        self.help_keywords = {
            "aide", "help", "aider", "commande", "commandes", "command", "commands",
            "quoi", "que", "faire", "comment", "utiliser", "usage"
        }
        
        # Patterns de normalisation
        self.accent_map = {
            'à': 'a', 'á': 'a', 'â': 'a', 'ä': 'a', 'ã': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        
        self.logger.info("CommandParser initialisé avec %d mots-clés de redémarrage", 
                        len(self.restart_keywords))
    
    def normalize_text(self, text: str) -> str:
        """
        Normalise le texte pour l'analyse
        
        Args:
            text: Texte à normaliser
            
        Returns:
            Texte normalisé (minuscules, sans accents, caractères spéciaux supprimés)
        """
        if not text:
            return ""
        
        # Convertir en minuscules
        text = text.lower().strip()
        
        # Supprimer les accents manuellement pour plus de contrôle
        for accent, replacement in self.accent_map.items():
            text = text.replace(accent, replacement)
        
        # Supprimer les caractères spéciaux et garder seulement lettres, chiffres, espaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normaliser les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def calculate_levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calcule la distance de Levenshtein entre deux chaînes
        (pour tolérance aux fautes d'orthographe)
        
        Args:
            s1: Première chaîne
            s2: Seconde chaîne
            
        Returns:
            Distance de Levenshtein (nombre de modifications nécessaires)
        """
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def find_similar_keywords(self, word: str, keywords: set, max_distance: int = 2) -> List[Tuple[str, int]]:
        """
        Trouve les mots-clés similaires avec distance de Levenshtein
        
        Args:
            word: Mot à analyser
            keywords: Set de mots-clés de référence
            max_distance: Distance maximale autorisée
            
        Returns:
            Liste de tuples (mot_cle, distance) triée par distance
        """
        similar = []
        
        for keyword in keywords:
            distance = self.calculate_levenshtein_distance(word, keyword)
            if distance <= max_distance:
                similar.append((keyword, distance))
        
        # Trier par distance (plus petite distance = plus similaire)
        similar.sort(key=lambda x: x[1])
        return similar
    
    def analyze_restart_intent(self, normalized_text: str) -> Tuple[float, List[str]]:
        """
        Analyse l'intention de redémarrage dans le texte
        
        Args:
            normalized_text: Texte normalisé à analyser
            
        Returns:
            Tuple (score_confiance, mots_cles_trouves)
        """
        words = normalized_text.split()
        matched_keywords = []
        restart_score = 0.0
        server_score = 0.0
        
        for word in words:
            # Recherche exacte dans les mots-clés de redémarrage
            if word in self.restart_keywords:
                matched_keywords.append(word)
                restart_score += 1.0
                continue
            
            # Recherche exacte dans les mots-clés de serveur
            if word in self.server_keywords:
                matched_keywords.append(word)
                server_score += 0.8
                continue
            
            # Recherche avec tolérance aux fautes (distance 1-2)
            restart_similar = self.find_similar_keywords(word, self.restart_keywords, max_distance=2)
            if restart_similar:
                best_match, distance = restart_similar[0]
                # Score inversement proportionnel à la distance
                score = 1.0 - (distance * 0.3)  # distance 1 = 0.7, distance 2 = 0.4
                if score > 0:
                    matched_keywords.append(f"{word}~{best_match}")
                    restart_score += score
                continue
            
            # Recherche serveur avec tolérance
            server_similar = self.find_similar_keywords(word, self.server_keywords, max_distance=2)
            if server_similar:
                best_match, distance = server_similar[0]
                score = 0.8 - (distance * 0.2)  # distance 1 = 0.6, distance 2 = 0.4
                if score > 0:
                    matched_keywords.append(f"{word}~{best_match}")
                    server_score += score
        
        # Calcul du score final
        # Il faut au moins un mot de redémarrage ET un mot de serveur pour un bon score
        if restart_score > 0 and server_score > 0:
            confidence = min(0.95, (restart_score + server_score) / 2)
        elif restart_score > 0:
            # Seulement des mots de redémarrage, score réduit
            confidence = min(0.7, restart_score * 0.5)
        else:
            confidence = 0.0
        
        return confidence, matched_keywords
    
    def analyze_help_intent(self, normalized_text: str) -> Tuple[float, List[str]]:
        """
        Analyse l'intention d'aide dans le texte
        
        Args:
            normalized_text: Texte normalisé à analyser
            
        Returns:
            Tuple (score_confiance, mots_cles_trouves)
        """
        words = normalized_text.split()
        matched_keywords = []
        help_score = 0.0
        
        for word in words:
            if word in self.help_keywords:
                matched_keywords.append(word)
                help_score += 1.0
                continue
            
            # Recherche avec tolérance aux fautes
            help_similar = self.find_similar_keywords(word, self.help_keywords, max_distance=1)
            if help_similar:
                best_match, distance = help_similar[0]
                score = 1.0 - (distance * 0.5)
                if score > 0:
                    matched_keywords.append(f"{word}~{best_match}")
                    help_score += score
        
        confidence = min(0.9, help_score * 0.8)
        return confidence, matched_keywords
    
    def detect_bot_mention(self, message_content: str, bot_name: str = "CubeGuardian", 
                         discord_message=None) -> bool:
        """
        Détecte si le message mentionne explicitement le bot
        Supporte les vraies mentions Discord (<@!bot_id>) et les mentions textuelles
        
        Args:
            message_content: Contenu du message
            bot_name: Nom du bot à rechercher
            discord_message: Objet message Discord (pour détecter les vraies mentions)
            
        Returns:
            True si le bot est mentionné
        """
        self.logger.debug(f"Détection mention - Message: '{message_content}'")
        
        # PRIORITÉ 1: Vraies mentions Discord (<@!bot_id> ou <@bot_id>)
        if discord_message and hasattr(discord_message, 'mentions'):
            for mention in discord_message.mentions:
                if mention.bot:  # C'est un bot mentionné
                    self.logger.debug(f"Vraie mention Discord détectée: {mention.name}")
                    return True
        
        # PRIORITÉ 2: Patterns de mention textuelle
        message_lower = message_content.lower()
        bot_name_lower = bot_name.lower()
        
        # Patterns de mention du bot
        mention_patterns = [
            f"@{bot_name_lower}",           # @CubeGuardian
            f"@ {bot_name_lower}",          # @ CubeGuardian
            f"{bot_name_lower}",            # CubeGuardian
            "bot",                          # bot
            "@bot",                         # @bot
            "hey bot",                      # hey bot
            "salut bot",                    # salut bot
        ]
        
        for pattern in mention_patterns:
            if pattern in message_lower:
                self.logger.debug(f"Mention textuelle détectée: '{pattern}'")
                return True
        
        self.logger.debug("Aucune mention détectée")
        return False

    def parse_command(self, message_content: str, bot_name: str = "CubeGuardian", 
                     require_mention: bool = True, discord_message=None) -> CommandResult:
        """
        Analyse un message pour détecter une commande
        
        Args:
            message_content: Contenu du message à analyser
            bot_name: Nom du bot (pour détecter les mentions)
            require_mention: Si True, exige une mention du bot pour les commandes
            
        Returns:
            Résultat de l'analyse avec intention et score de confiance
        """
        if not message_content or not message_content.strip():
            return CommandResult(
                intent=CommandIntent.UNKNOWN,
                confidence=0.0,
                matched_keywords=[],
                original_text="",
                normalized_text=""
            )
        
        original_text = message_content.strip()
        normalized_text = self.normalize_text(original_text)
        
        self.logger.debug(f"Analyse du message: '{original_text}' -> '{normalized_text}'")
        
        # Vérification de mention du bot pour les commandes sensibles
        has_bot_mention = self.detect_bot_mention(original_text, bot_name, discord_message)
        
        # Analyse des différentes intentions
        restart_confidence, restart_keywords = self.analyze_restart_intent(normalized_text)
        help_confidence, help_keywords = self.analyze_help_intent(normalized_text)
        
        # SÉCURITÉ : Appliquer la règle de mention pour les commandes de redémarrage
        if require_mention and restart_confidence >= 0.5:
            if not has_bot_mention:
                # Réduire drastiquement le score si pas de mention du bot
                restart_confidence *= 0.1  # Réduction de 90%
                restart_keywords.insert(0, "NO_BOT_MENTION")
                self.logger.info(f"Commande potentielle sans mention du bot - Score réduit: {restart_confidence:.2f}")
        
        # Déterminer l'intention principale
        if restart_confidence >= 0.5:  # Seuil pour redémarrage
            return CommandResult(
                intent=CommandIntent.RESTART_MINECRAFT,
                confidence=restart_confidence,
                matched_keywords=restart_keywords,
                original_text=original_text,
                normalized_text=normalized_text
            )
        elif help_confidence >= 0.6:  # Seuil pour aide
            return CommandResult(
                intent=CommandIntent.HELP,
                confidence=help_confidence,
                matched_keywords=help_keywords,
                original_text=original_text,
                normalized_text=normalized_text
            )
        else:
            return CommandResult(
                intent=CommandIntent.UNKNOWN,
                confidence=max(restart_confidence, help_confidence),
                matched_keywords=restart_keywords + help_keywords,
                original_text=original_text,
                normalized_text=normalized_text
            )
    
    def get_help_response(self) -> str:
        """
        Retourne le message d'aide pour les commandes
        
        Returns:
            Message d'aide formaté
        """
        return """🆘 **Aide - Commandes disponibles**

🎮 **Redémarrer Minecraft :** Mentionnez-moi avec une phrase comme :
   • "@CubeGuardian redémarrer le serveur minecraft"
   • "@CubeGuardian restart minecraft"
   • "@CubeGuardian reboot serveur"

📝 **Variantes acceptées :**
   • redémarrer, restart, reboot, relancer
   • serveur, server, minecraft, mc

⚠️ **Restrictions :**
   • Seuls les joueurs autorisés peuvent utiliser les commandes
   • Cooldown de 10 minutes entre les commandes
   • Confirmation requise avant exécution

💡 **Astuce :** Le bot tolère les fautes d'orthographe !"""
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Retourne les statistiques du parser
        
        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            'restart_keywords_count': len(self.restart_keywords),
            'server_keywords_count': len(self.server_keywords),
            'help_keywords_count': len(self.help_keywords),
            'total_keywords': len(self.restart_keywords) + len(self.server_keywords) + len(self.help_keywords)
        }
    
    def __str__(self) -> str:
        """Représentation string du parser"""
        stats = self.get_statistics()
        return f"CommandParser(keywords={stats['total_keywords']}, restart={stats['restart_keywords_count']})"
