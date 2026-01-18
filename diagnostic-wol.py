#!/usr/bin/env python3
"""
Script de diagnostic Wake-on-LAN pour Bot CubeGuardian
Compare differentes methodes d'envoi de Magic Packet
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

async def test_wake_on_lan_methods():
    """Test differentes methodes de Wake-on-LAN"""
    print('=' * 60)
    print('DIAGNOSTIC WAKE-ON-LAN - Bot CubeGuardian')
    print('=' * 60)
    
    logger = logging.getLogger('diagnostic')
    wake_manager = WakeOnLANManager(logger)
    
    # Configuration du serveur
    mac_address = '00:23:7D:FD:C0:5C'
    target_host = '192.168.1.245'
    
    print(f'Adresse MAC: {mac_address}')
    print(f'Adresse IP: {target_host}')
    print()
    
    # Test 1: Methode actuelle du bot
    print('TEST 1: Methode actuelle du bot (wakeonlan module)')
    print('-' * 50)
    try:
        result = await wake_manager.wake_server(mac_address, target_host)
        print(f'Resultat: {result["message"]}')
        print(f'Succes: {result["success"]}')
        print(f'Timestamp: {result["timestamp"]}')
        if 'details' in result:
            print(f'Details: {result["details"]}')
    except Exception as e:
        print(f'Erreur: {e}')
    print()
    
    # Test 2: Test direct avec wakeonlan
    print('TEST 2: Test direct avec module wakeonlan')
    print('-' * 50)
    try:
        from wakeonlan import send_magic_packet
        print('Envoi du Magic Packet...')
        send_magic_packet(mac_address)
        print('Magic Packet envoye avec succes (module wakeonlan)')
    except ImportError as e:
        print(f'Module wakeonlan non installe: {e}')
    except Exception as e:
        print(f'Erreur: {e}')
    print()
    
    # Test 3: Test avec broadcast explicite
    print('TEST 3: Test avec broadcast explicite')
    print('-' * 50)
    try:
        from wakeonlan import send_magic_packet
        print('Envoi du Magic Packet avec broadcast explicite...')
        send_magic_packet(mac_address, ip_address='255.255.255.255')
        print('Magic Packet envoye avec broadcast explicite')
    except Exception as e:
        print(f'Erreur: {e}')
    print()
    
    # Test 4: Test avec interface reseau specifique
    print('TEST 4: Test avec interface reseau specifique')
    print('-' * 50)
    try:
        from wakeonlan import send_magic_packet
        print('Envoi du Magic Packet avec interface reseau...')
        send_magic_packet(mac_address, ip_address='192.168.1.255')
        print('Magic Packet envoye avec interface reseau')
    except Exception as e:
        print(f'Erreur: {e}')
    print()
    
    # Test 5: Verification de la configuration reseau
    print('TEST 5: Verification de la configuration reseau')
    print('-' * 50)
    try:
        import socket
        import subprocess
        
        # Obtenir l'interface reseau locale
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        print('Configuration reseau Windows:')
        print(result.stdout[:500] + '...' if len(result.stdout) > 500 else result.stdout)
        
    except Exception as e:
        print(f'Erreur lors de la verification reseau: {e}')
    print()
    
    print('=' * 60)
    print('RECOMMANDATIONS:')
    print('=' * 60)
    print('1. Verifiez que le serveur a le Wake-on-LAN active dans le BIOS')
    print('2. Verifiez que la carte reseau supporte le WOL')
    print('3. Testez avec wakemeonlan-x64 pour confirmer que le WOL fonctionne')
    print('4. Verifiez que le firewall ne bloque pas les paquets UDP')
    print('5. Essayez differentes adresses de broadcast (255.255.255.255, 192.168.1.255)')
    print()

if __name__ == "__main__":
    asyncio.run(test_wake_on_lan_methods())
