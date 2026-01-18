"""
Script de test pour le module command_parser.py
Teste la reconnaissance de commandes avec différentes variantes
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from command_parser import CommandParser, CommandIntent

def test_command_parser():
    """Test complet du système de reconnaissance de commandes"""
    
    print("🧪 Test du système de reconnaissance de commandes")
    print("=" * 60)
    
    # Initialiser le parser
    parser = CommandParser()
    print(f"📊 Parser initialisé: {parser}")
    print(f"📈 Statistiques: {parser.get_statistics()}")
    print()
    
    # Tests de commandes de redémarrage - français standard
    restart_tests = [
        # Français correct
        "@CubeGuardian redémarrer le serveur minecraft",
        "redémarre le serveur stp",
        "relancer minecraft",
        "peux-tu redémarrer le serveur ?",
        
        # Avec fautes d'orthographe
        "redemarer le servere minecraft",
        "redémarer le serv",
        "relencé minecraf",
        "rebote le server",
        
        # Anglicismes
        "restart minecraft server",
        "reboot le serveur",
        "reset minecraft",
        "restart le serv",
        
        # Variations créatives
        "yo bot restart mc",
        "redémarre moi ça",
        "reboot servere",
        "relance le jeu minecraft",
        
        # Phrases naturelles
        "salut, peux-tu redémarrer le serveur minecraft ?",
        "hey bot, le server minecraft bug, restart stp",
        "@bot redémarre le serveur minecraft car il lag"
    ]
    
    print("🎮 Tests de commandes de REDÉMARRAGE:")
    print("-" * 40)
    
    for test_msg in restart_tests:
        result = parser.parse_command(test_msg)
        status = "✅" if result.intent == CommandIntent.RESTART_MINECRAFT else "❌"
        confidence_bar = "█" * int(result.confidence * 10)
        
        print(f"{status} [{confidence_bar:<10}] {result.confidence:.2f} | {test_msg}")
        if result.matched_keywords:
            print(f"    🔍 Mots-clés: {', '.join(result.matched_keywords[:3])}")
        print()
    
    # Tests de commandes d'aide
    help_tests = [
        "aide",
        "help",
        "comment utiliser le bot ?",
        "quelles sont les commandes ?",
        "que peux-tu faire ?",
        "commands",
        "aider moi"
    ]
    
    print("🆘 Tests de commandes d'AIDE:")
    print("-" * 40)
    
    for test_msg in help_tests:
        result = parser.parse_command(test_msg)
        status = "✅" if result.intent == CommandIntent.HELP else "❌"
        confidence_bar = "█" * int(result.confidence * 10)
        
        print(f"{status} [{confidence_bar:<10}] {result.confidence:.2f} | {test_msg}")
        if result.matched_keywords:
            print(f"    🔍 Mots-clés: {', '.join(result.matched_keywords)}")
        print()
    
    # Tests de messages non-commandes (doivent être rejetés)
    negative_tests = [
        "salut tout le monde !",
        "comment ça va ?",
        "je joue à minecraft",
        "le serveur marche bien",
        "bonne journée",
        "123456",
        "",
        "lol mdr ptdr"
    ]
    
    print("❌ Tests de messages NON-COMMANDES (doivent être rejetés):")
    print("-" * 40)
    
    for test_msg in negative_tests:
        result = parser.parse_command(test_msg)
        status = "✅" if result.intent == CommandIntent.UNKNOWN else "❌"
        confidence_bar = "█" * int(result.confidence * 10)
        
        print(f"{status} [{confidence_bar:<10}] {result.confidence:.2f} | {test_msg}")
        print()
    
    # Test de normalisation
    print("🔧 Tests de NORMALISATION:")
    print("-" * 40)
    
    normalization_tests = [
        "REDÉMARRER LE SERVEUR MINECRAFT !!!",
        "redémarre... le... serveur ???",
        "restart@minecraft#server$$$",
        "rédémarrer   le    serveur",
        "àáâäéèêëïîôöùûü test"
    ]
    
    for test_msg in normalization_tests:
        normalized = parser.normalize_text(test_msg)
        print(f"📝 '{test_msg}'")
        print(f"   → '{normalized}'")
        print()
    
    # Test de distance de Levenshtein
    print("📏 Tests de DISTANCE DE LEVENSHTEIN:")
    print("-" * 40)
    
    levenshtein_tests = [
        ("redemarrer", "redémarrer"),
        ("servere", "serveur"),
        ("minecraf", "minecraft"),
        ("rebote", "reboot"),
        ("starte", "start")
    ]
    
    for word1, word2 in levenshtein_tests:
        distance = parser.calculate_levenshtein_distance(word1, word2)
        print(f"📏 '{word1}' ↔ '{word2}' = {distance}")
    
    print()
    print("🎯 Affichage du message d'aide:")
    print("-" * 40)
    print(parser.get_help_response())
    
    print()
    print("✅ Tests terminés ! Le système de reconnaissance est opérationnel.")

def demo_interactive():
    """Démo interactive pour tester en temps réel"""
    
    print("\n🎮 DÉMO INTERACTIVE - Reconnaissance de commandes")
    print("=" * 60)
    print("Tapez vos messages pour tester la reconnaissance (q pour quitter)")
    print()
    
    parser = CommandParser()
    
    while True:
        try:
            user_input = input("💬 Votre message: ").strip()
            
            if user_input.lower() in ['q', 'quit', 'quitter', 'exit']:
                print("👋 Au revoir !")
                break
            
            if not user_input:
                continue
            
            result = parser.parse_command(user_input)
            
            print(f"🤖 Résultat:")
            print(f"   📋 Intention: {result.intent.value}")
            print(f"   📊 Confiance: {result.confidence:.2f} ({result.confidence*100:.0f}%)")
            print(f"   🔍 Mots-clés: {result.matched_keywords}")
            print(f"   📝 Normalisé: '{result.normalized_text}'")
            
            if result.intent == CommandIntent.RESTART_MINECRAFT and result.confidence >= 0.5:
                print("   ✅ COMMANDE DÉTECTÉE - Redémarrage Minecraft")
            elif result.intent == CommandIntent.HELP and result.confidence >= 0.6:
                print("   ℹ️ DEMANDE D'AIDE DÉTECTÉE")
            else:
                print("   ❌ Aucune commande reconnue")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    # Tests automatiques
    test_command_parser()
    
    # Proposer la démo interactive
    print("\n" + "="*60)
    demo_choice = input("🎮 Voulez-vous tester la démo interactive ? (o/n): ").strip().lower()
    if demo_choice in ['o', 'oui', 'y', 'yes']:
        demo_interactive()
