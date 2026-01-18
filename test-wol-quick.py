#!/usr/bin/env python3
"""
Test rapide du Wake-on-LAN ameliore
"""

import asyncio
import sys
import logging

# Ajouter src au path
sys.path.insert(0, 'src')

from server_manager.wake_on_lan import WakeOnLANManager

async def quick_test():
    """Test rapide du Wake-on-LAN"""
    print('Test rapide Wake-on-LAN ameliore...')
    
    logger = logging.getLogger('quick_test')
    logger.setLevel(logging.INFO)
    
    wake_manager = WakeOnLANManager(logger)
    
    # Configuration
    mac_address = '00:23:7D:FD:C0:5C'
    target_host = '192.168.1.245'
    
    print(f'Envoi Magic Packet vers {target_host} ({mac_address})...')
    
    result = await wake_manager.wake_server(mac_address, target_host)
    
    print(f'Resultat: {result["message"]}')
    print(f'Succes: {result["success"]}')
    
    if 'details' in result:
        details = result['details']
        print(f'Methodes: {details.get("methods_used")}')
        print(f'Succes: {details.get("success_count")}')

if __name__ == "__main__":
    asyncio.run(quick_test())
