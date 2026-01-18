#!/usr/bin/env python3
"""
Test rapide des nouvelles fonctionnalités NLP dans le conteneur Docker
"""

def test_nlp_dependencies():
    """Test des dépendances NLP"""
    print("🔧 Test des dépendances NLP...")
    
    try:
        # Test fuzzywuzzy
        from fuzzywuzzy import fuzz
        score = fuzz.ratio("redemarrer", "redémarrer")
        print(f"✅ fuzzywuzzy: ratio('redemarrer', 'redémarrer') = {score}")
        
        # Test python-Levenshtein
        from fuzzywuzzy import process
        choices = ["redemarrer", "restart", "reboot"]
        result = process.extractOne("redémarrer", choices)
        print(f"✅ python-Levenshtein: extractOne('redémarrer', {choices}) = {result}")
        
        # Test unicodedata (built-in)
        import unicodedata
        normalized = unicodedata.normalize('NFD', 'redémarrer')
        print(f"✅ unicodedata: normalize('NFD', 'redémarrer') = {repr(normalized)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_command_parser():
    """Test du module CommandParser"""
    print("\n🔧 Test du module CommandParser...")
    
    try:
        from src.command_parser import CommandParser, CommandIntent
        
        parser = CommandParser()
        
        # Test 1: Commande claire
        result1 = parser.parse_command("@CubeGuardian redémarrer le serveur minecraft")
        print(f"✅ Test 1: '{result1.intent}' (confiance: {result1.confidence:.2f})")
        
        # Test 2: Commande avec fautes
        result2 = parser.parse_command("@bot restart minecraft svp")
        print(f"✅ Test 2: '{result2.intent}' (confiance: {result2.confidence:.2f})")
        
        # Test 3: Discussion normale (sans mention)
        result3 = parser.parse_command("on pourrait redémarrer minecraft plus tard", require_mention=True)
        print(f"✅ Test 3: '{result3.intent}' (confiance: {result3.confidence:.2f})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import CommandParser: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur CommandParser: {e}")
        return False

def test_security_manager():
    """Test du module SecurityManager"""
    print("\n🔧 Test du module SecurityManager...")
    
    try:
        from src.security_manager import SecurityManager
        from unittest.mock import Mock
        
        # Mock config et log managers
        config_manager = Mock()
        log_manager = Mock()
        
        security = SecurityManager(config_manager, log_manager)
        
        # Test cooldown
        user_id = 12345
        print(f"✅ Cooldown initial: {security.check_user_cooldown(user_id)}")
        
        security.update_user_cooldown(user_id)
        print(f"✅ Cooldown après update: {security.check_user_cooldown(user_id)}")
        
        remaining = security.get_user_cooldown_remaining(user_id)
        print(f"✅ Temps restant: {remaining}s")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import SecurityManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur SecurityManager: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 TEST DE MISE À JOUR DOCKER - Version 2.1.0\n")
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Dépendances NLP
    if test_nlp_dependencies():
        success_count += 1
    
    # Test 2: CommandParser  
    if test_command_parser():
        success_count += 1
    
    # Test 3: SecurityManager
    if test_security_manager():
        success_count += 1
    
    # Résultat final
    print(f"\n🎯 RÉSULTAT: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("✅ SUCCÈS: Tous les modules fonctionnent!")
        print("🎮 Le bot est prêt pour les commandes de redémarrage Minecraft!")
    else:
        print("❌ ÉCHEC: Certains modules ne fonctionnent pas correctement.")
        print("🔧 Vérifiez l'installation des dépendances Docker.")

if __name__ == "__main__":
    main()
