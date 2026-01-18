#!/usr/bin/env python3
"""
Test de la version amelioree du Wake-on-LAN
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

async def test_enhanced_wake_on_lan():
    """Test de la version amelioree du Wake-on-LAN"""
    print('=' * 60)
    print('TEST WAKE-ON-LAN AMELIORE - Bot CubeGuardian')
    print('=' * 60)
    
    logger = logging.getLogger('test_enhanced')
    wake_manager = WakeOnLANManager(logger)
    
    # Configuration du serveur
    mac_address = '00:23:7D:FD:C0:5C'
    target_host = '192.168.1.245'
    
    print(f'Adresse MAC: {mac_address}')
    print(f'Adresse IP: {target_host}')
    print()
    
    print('Test de la version amelioree...')
    print('-' * 40)
    
    try:
        result = await wake_manager.wake_server(mac_address, target_host)
        
        print(f'Resultat: {result["message"]}')
        print(f'Succes: {result["success"]}')
        print(f'Timestamp: {result["timestamp"]}')
        
        if 'details' in result:
            details = result['details']
            print(f'Adresse MAC: {details.get("mac_address")}')
            print(f'Adresse IP: {details.get("target_host")}')
            print(f'Methodes utilisees: {details.get("methods_used")}')
            print(f'Nombre de succes: {details.get("success_count")}')
        
        if 'error' in result:
            print(f'Erreur: {result["error"]}')
            
    except Exception as e:
        print(f'Erreur lors du test: {e}')
    
    print()
    print('=' * 60)
    print('RECOMMANDATIONS:')
    print('=' * 60)
    print('1. Verifiez que le serveur est bien eteint avant le test')
    print('2. Attendez quelques secondes apres l\'envoi du paquet')
    print('3. Verifiez que le serveur demarre (LED, ventilateurs, etc.)')
    print('4. Comparez avec wakemeonlan-x64 pour validation')
    print()

if __name__ == "__main__":
    asyncio.run(test_enhanced_wake_on_lan())
