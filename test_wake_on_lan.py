#!/usr/bin/env python3
"""
Test du Wake-on-LAN pour Bot CubeGuardian
"""

import sys
import asyncio
import logging

# Ajouter src au path
sys.path.insert(0, 'src')

from server_manager.wake_on_lan import WakeOnLANManager

async def test_wake_on_lan():
    """Test du Wake-on-LAN"""
    print('🧪 Test du Wake-on-LAN...')
    
    logger = logging.getLogger('test')
    wake_manager = WakeOnLANManager(logger)
    
    # Test avec l'adresse MAC de ton serveur
    mac_address = '00:23:7D:FD:C0:5C'
    target_host = '192.168.1.245'
    
    print(f'🔄 Envoi du Magic Packet vers {target_host} ({mac_address})...')
    
    try:
        result = await wake_manager.wake_server(mac_address, target_host)
        print(f'✅ Résultat: {result["message"]}')
        print(f'✅ Succès: {result["success"]}')
        print(f'✅ Timestamp: {result["timestamp"]}')
    except Exception as e:
        print(f'❌ Erreur: {e}')

if __name__ == "__main__":
    asyncio.run(test_wake_on_lan())
