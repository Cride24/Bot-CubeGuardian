#!/usr/bin/env python3
"""
Test de simulation d'échec Wake-on-LAN pour vérifier les messages d'erreur
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

async def test_wol_error_simulation():
    """Test de simulation d'échec Wake-on-LAN"""
    print('=' * 60)
    print('TEST SIMULATION ECHEC WAKE-ON-LAN')
    print('=' * 60)
    
    logger = logging.getLogger('test_error')
    wake_manager = WakeOnLANManager(logger)
    
    # Test 1: Adresse MAC invalide pour simuler un échec
    print('TEST 1: Adresse MAC invalide (simulation échec)')
    print('-' * 50)
    
    try:
        result = await wake_manager.wake_server("00:00:00:00:00:00", "192.168.1.999")
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
            
    except Exception as e:
        print(f'Erreur lors du test: {e}')
    
    print()
    
    # Test 2: Adresse MAC valide mais serveur inexistant
    print('TEST 2: Adresse MAC valide mais serveur inexistant')
    print('-' * 50)
    
    try:
        result = await wake_manager.wake_server("00:23:7D:FD:C0:5C", "192.168.1.999")
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
            
    except Exception as e:
        print(f'Erreur lors du test: {e}')
    
    print()
    print('=' * 60)
    print('VERIFICATION DES MESSAGES D\'ERREUR:')
    print('=' * 60)
    print('1. Le bot doit maintenant envoyer un message d\'erreur dans le salon textuel')
    print('2. Le message doit contenir l\'adresse IP et l\'erreur détaillée')
    print('3. Le message doit indiquer que le serveur ne démarrera pas automatiquement')
    print()

if __name__ == "__main__":
    asyncio.run(test_wol_error_simulation())
