#!/usr/bin/env python3
"""
Test de connectivité pour diagnostiquer le problème
"""

import asyncio
import sys
import logging

# Ajouter src au path
sys.path.insert(0, 'src')

from server_manager.connectivity_checker import ConnectivityChecker
from server_manager.minecraft_checker import MinecraftChecker

async def test_connectivity():
    """Test de connectivité des serveurs"""
    print('=' * 60)
    print('TEST DE CONNECTIVITE - DIAGNOSTIC')
    print('=' * 60)
    
    logger = logging.getLogger('test_connectivity')
    logger.setLevel(logging.INFO)
    
    connectivity_checker = ConnectivityChecker(logger)
    minecraft_checker = MinecraftChecker(logger)
    
    # Test 1: Connectivité Proxmox
    print('TEST 1: Connectivité Proxmox (192.168.1.245:8006)')
    print('-' * 50)
    
    proxmox_result = await connectivity_checker.check_proxmox_connectivity('192.168.1.245')
    print(f'Proxmox accessible: {proxmox_result["success"]}')
    print(f'Message: {proxmox_result["message"]}')
    if 'details' in proxmox_result:
        print(f'Détails: {proxmox_result["details"]}')
    print()
    
    # Test 2: Connectivité Minecraft
    print('TEST 2: Connectivité Minecraft (192.168.1.105:25565)')
    print('-' * 50)
    
    minecraft_result = await minecraft_checker.check_minecraft_connectivity('192.168.1.105', 25565)
    print(f'Minecraft accessible: {minecraft_result["success"]}')
    print(f'Message: {minecraft_result["message"]}')
    if 'details' in minecraft_result:
        print(f'Détails: {minecraft_result["details"]}')
    print()
    
    # Test 3: Ping simple
    print('TEST 3: Ping simple vers les serveurs')
    print('-' * 50)
    
    import subprocess
    try:
        # Ping Proxmox
        result = subprocess.run(['ping', '-c', '1', '192.168.1.245'], 
                              capture_output=True, text=True, timeout=5)
        print(f'Ping Proxmox (192.168.1.245): {"OK" if result.returncode == 0 else "ÉCHEC"}')
        
        # Ping Minecraft
        result = subprocess.run(['ping', '-c', '1', '192.168.1.105'], 
                              capture_output=True, text=True, timeout=5)
        print(f'Ping Minecraft (192.168.1.105): {"OK" if result.returncode == 0 else "ÉCHEC"}')
        
    except Exception as e:
        print(f'Erreur ping: {e}')
    
    print()
    print('=' * 60)
    print('ANALYSE:')
    print('=' * 60)
    
    if minecraft_result["success"]:
        print('✅ Minecraft est accessible - Le serveur est déjà en cours d\'exécution')
        print('✅ Le bot ne démarrera pas le serveur car il considère qu\'il est déjà UP')
        print('✅ C\'est le comportement normal du bot')
    else:
        print('❌ Minecraft n\'est pas accessible - Le serveur devrait être démarré')
        print('❌ Il y a peut-être un problème avec la détection de connectivité')
    
    if proxmox_result["success"]:
        print('✅ Proxmox est accessible - Le serveur hôte est UP')
    else:
        print('❌ Proxmox n\'est pas accessible - Le serveur hôte est DOWN')

if __name__ == "__main__":
    asyncio.run(test_connectivity())
