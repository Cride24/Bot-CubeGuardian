#!/usr/bin/env python3
"""
Tests unitaires pour la configuration du Bot CubeGuardian
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_manager import ConfigManager

def test_config_loading():
    """Test du chargement de la configuration"""
    print("Test du chargement de la configuration...")
    
    try:
        config = ConfigManager("./config")
        
        # Vérifier que les sections sont chargées
        assert 'bot' in config.config, "Section 'bot' manquante"
        assert 'discord' in config.config, "Section 'discord' manquante"
        assert 'servers' in config.config, "Section 'servers' manquante"
        assert 'messages' in config.config, "Section 'messages' manquante"
        
        print("✅ Configuration chargée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement de la configuration: {e}")
        return False

def test_config_values():
    """Test des valeurs de configuration"""
    print("Test des valeurs de configuration...")
    
    try:
        config = ConfigManager("./config")
        
        # Test des valeurs de base
        bot_name = config.get_config('bot.name')
        assert bot_name == "CubeGuardian", f"Nom du bot incorrect: {bot_name}"
        
        bot_version = config.get_config('bot.version')
        assert bot_version == "1.1.0", f"Version du bot incorrecte: {bot_version}"
        
        # Test des timers
        startup_timeout = config.get_timer('startup_timeout')
        assert startup_timeout == 600, f"Timeout de démarrage incorrect: {startup_timeout}"
        
        shutdown_delay = config.get_timer('shutdown_delay')
        assert shutdown_delay == 600, f"Délai d'arrêt incorrect: {shutdown_delay}"
        
        print("✅ Valeurs de configuration correctes")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des valeurs: {e}")
        return False

def test_messages():
    """Test des messages"""
    print("Test des messages...")
    
    try:
        config = ConfigManager("./config")
        
        # Test de récupération de message
        startup_message = config.get_message('startup.request', user="TestUser")
        assert "TestUser" in startup_message, "Message de démarrage incorrect"
        
        shutdown_message = config.get_message('shutdown.initiated', delay=10)
        assert "10" in shutdown_message, "Message d'arrêt incorrect"
        
        print("✅ Messages corrects")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des messages: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Tests de configuration du Bot CubeGuardian")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_config_values,
        test_messages
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test échoué: {e}")
            results.append(False)
        print()
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print("📊 Résumé des tests:")
    print("=" * 50)
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests sont passés!")
        return 0
    else:
        print("⚠️ Certains tests ont échoué.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
