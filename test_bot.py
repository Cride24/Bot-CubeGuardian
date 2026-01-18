#!/usr/bin/env python3
"""
Script de test pour Bot CubeGuardian
Teste les fonctionnalités de base sans connexion Discord
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_manager import ConfigManager
from log_manager import LogManager
from server_manager_interface import ServerManager
from user_manager import UserManager
from message_manager import MessageManager

async def test_config_manager():
    """Test du gestionnaire de configuration"""
    print("🔧 Test du ConfigManager...")
    
    try:
        config = ConfigManager("./config")
        
        # Test de validation
        is_valid = config.validate_config()
        print(f"   Configuration valide: {is_valid}")
        
        # Test de récupération de valeurs
        bot_name = config.get_config('bot.name')
        print(f"   Nom du bot: {bot_name}")
        
        # Test des utilisateurs autorisés
        authorized_users = config.get_authorized_users()
        print(f"   Utilisateurs autorisés: {len(authorized_users)}")
        
        print("   ✅ ConfigManager: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ ConfigManager: ERREUR - {e}")
        return False

async def test_log_manager():
    """Test du gestionnaire de logs"""
    print("📝 Test du LogManager...")
    
    try:
        config = ConfigManager("./config")
        log_config = config.get_config('logging', {})
        
        log_manager = LogManager(log_config)
        
        # Test des logs
        log_manager.log_info("Test d'information")
        log_manager.log_warning("Test d'avertissement")
        log_manager.log_error("Test d'erreur")
        
        # Test des logs spécialisés
        log_manager.log_voice_event("test", "TestUser", "TestChannel")
        log_manager.log_server_event("test", "TestServer", "Test details")
        
        print("   ✅ LogManager: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ LogManager: ERREUR - {e}")
        return False

async def test_user_manager():
    """Test du gestionnaire d'utilisateurs"""
    print("👥 Test du UserManager...")
    
    try:
        config = ConfigManager("./config")
        log_config = config.get_config('logging', {})
        log_manager = LogManager(log_config)
        
        user_manager = UserManager(config, log_manager)
        
        # Test d'autorisation
        test_user_id = 123456789012345678
        is_authorized = user_manager.is_authorized(test_user_id)
        print(f"   Utilisateur {test_user_id} autorisé: {is_authorized}")
        
        # Test des permissions
        permissions = user_manager.get_user_permissions(test_user_id)
        print(f"   Permissions: {permissions}")
        
        # Test des statistiques
        stats = user_manager.get_statistics()
        print(f"   Statistiques: {stats}")
        
        print("   ✅ UserManager: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ UserManager: ERREUR - {e}")
        return False

async def test_server_manager():
    """Test du gestionnaire de serveurs"""
    print("🖥️ Test du ServerManager...")
    
    try:
        config = ConfigManager("./config")
        log_config = config.get_config('logging', {})
        log_manager = LogManager(log_config)
        
        server_manager = ServerManager(config, log_manager)
        
        # Test de la configuration des serveurs
        proxmox_config = server_manager.proxmox_config
        minecraft_config = server_manager.minecraft_config
        
        print(f"   Serveur Proxmox: {proxmox_config.name} ({proxmox_config.ipv4})")
        print(f"   Serveur Minecraft: {minecraft_config.name} ({minecraft_config.ipv4}:{minecraft_config.port})")
        
        # Test des informations des serveurs
        server_info = server_manager.get_server_info()
        print(f"   Informations serveurs: {server_info}")
        
        print("   ✅ ServerManager: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ ServerManager: ERREUR - {e}")
        return False

async def test_powershell_scripts():
    """Test des scripts PowerShell"""
    print("🔧 Test des scripts PowerShell...")
    
    try:
        config = ConfigManager("./config")
        log_config = config.get_config('logging', {})
        log_manager = LogManager(log_config)
        
        server_manager = ServerManager(config, log_manager)
        
        # Test de vérification Proxmox (sans connexion réelle)
        print("   Test de vérification Proxmox...")
        result = await server_manager.check_proxmox_status()
        print(f"   Proxmox accessible: {result}")
        
        # Test de vérification Minecraft (sans connexion réelle)
        print("   Test de vérification Minecraft...")
        result = await server_manager.check_minecraft_status()
        print(f"   Minecraft accessible: {result}")
        
        print("   ✅ Scripts PowerShell: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ Scripts PowerShell: ERREUR - {e}")
        return False

async def test_message_manager():
    """Test du gestionnaire de messages"""
    print("💬 Test du MessageManager...")
    
    try:
        config = ConfigManager("./config")
        log_config = config.get_config('logging', {})
        log_manager = LogManager(log_config)
        
        message_manager = MessageManager(config, log_manager)
        
        # Test de récupération de messages
        startup_message = config.get_message('startup.request', user="TestUser")
        print(f"   Message de démarrage: {startup_message}")
        
        shutdown_message = config.get_message('shutdown.initiated', delay=10)
        print(f"   Message d'arrêt: {shutdown_message}")
        
        # Test de formatage
        formatted = message_manager.format_message(
            "Test message with {variable}",
            {"variable": "test_value"}
        )
        print(f"   Message formaté: {formatted}")
        
        print("   ✅ MessageManager: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ MessageManager: ERREUR - {e}")
        return False

async def main():
    """Fonction principale de test"""
    print("🤖 Test de Bot CubeGuardian")
    print("=" * 50)
    
    tests = [
        test_config_manager,
        test_log_manager,
        test_user_manager,
        test_server_manager,
        test_powershell_scripts,
        test_message_manager
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test échoué: {e}")
            results.append(False)
        print()
    
    # Résumé des tests
    print("📊 Résumé des tests:")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\nRésultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès!")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)
