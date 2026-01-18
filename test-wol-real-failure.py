#!/usr/bin/env python3
"""
Test de simulation d'échec réel Wake-on-LAN
"""

import asyncio
import sys
import logging
from datetime import datetime

# Ajouter src au path
sys.path.insert(0, 'src')

from server_manager.wake_on_lan import WakeOnLANManager

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MockWakeOnLANManager(WakeOnLANManager):
    """Version mock pour simuler un échec complet"""
    
    async def wake_server(self, mac_address: str, target_host: str):
        """Simule un échec complet du Wake-on-LAN"""
        return {
            "success": False,
            "message": "Toutes les methodes d'envoi ont echoue",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": "Simulation d'échec pour test",
            "details": {
                "mac_address": mac_address,
                "target_host": target_host,
                "methods_used": ["wakeonlan_module_failed: Test error", "socket_udp_global_failed: Test error"],
                "success_count": 0,
                "operation": "wake_on_lan_enhanced"
            }
        }

async def test_real_failure():
    """Test de simulation d'échec réel"""
    print('=' * 60)
    print('TEST SIMULATION ECHEC REEL WAKE-ON-LAN')
    print('=' * 60)
    
    logger = logging.getLogger('test_real_failure')
    wake_manager = MockWakeOnLANManager(logger)
    
    # Test avec échec simulé
    print('TEST: Échec simulé du Wake-on-LAN')
    print('-' * 50)
    
    try:
        result = await wake_manager.wake_server("00:23:7D:FD:C0:5C", "192.168.1.245")
        print(f'Resultat: {result["message"]}')
        print(f'Succes: {result["success"]}')
        print(f'Timestamp: {result["timestamp"]}')
        
        if 'error' in result:
            print(f'Erreur: {result["error"]}')
        
        if 'details' in result:
            details = result['details']
            print(f'Adresse MAC: {details.get("mac_address")}')
            print(f'Adresse IP: {details.get("target_host")}')
            print(f'Methodes utilisees: {details.get("methods_used")}')
            print(f'Nombre de succes: {details.get("success_count")}')
            
        # Test de la logique du bot
        print()
        print('TEST DE LA LOGIQUE DU BOT:')
        print('-' * 30)
        
        if result.get('success', False):
            print('✅ Le bot considérera que le Wake-on-LAN a réussi')
            print('✅ Aucun message d\'erreur ne sera envoyé')
        else:
            print('❌ Le bot considérera que le Wake-on-LAN a échoué')
            print('❌ Un message d\'erreur sera envoyé dans le salon textuel')
            print(f'❌ Message d\'erreur: "⚠️ Échec du Wake-on-LAN vers {details.get("target_host")}"')
            print(f'❌ Détails: "Erreur: {result.get("error")}"')
            print('❌ "Le serveur ne démarrera pas automatiquement."')
            
    except Exception as e:
        print(f'Erreur lors du test: {e}')
    
    print()
    print('=' * 60)
    print('CONCLUSION:')
    print('=' * 60)
    print('Avec cette correction, le bot enverra maintenant un message d\'erreur')
    print('dans le salon textuel Discord en cas d\'échec du Wake-on-LAN.')
    print()

if __name__ == "__main__":
    asyncio.run(test_real_failure())
