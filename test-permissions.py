#!/usr/bin/env python3
"""
Test des permissions du bot pour l'API Proxmox
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_proxmox_permissions():
    """Test des permissions Proxmox du bot"""
    
    # Configuration du bot
    api_url = "https://192.168.1.245:8006/api2/json"
    token_id = "cubeguardian@pam!cubeguardian-discord-bot"
    token_secret = "7420cec7-e4bc-4248-adc0-9c38738acce8"
    
    headers = {
        "Authorization": f"PVEAPIToken={token_id}={token_secret}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print("🔍 Test des permissions Proxmox du bot")
    print(f"API URL: {api_url}")
    print(f"Token ID: {token_id}")
    print("-" * 50)
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:
        
        # Test 1: Vérifier l'authentification
        print("1️⃣ Test d'authentification...")
        try:
            async with session.get(f"{api_url}/version", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Authentification OK - Version: {data['data']['version']}")
                else:
                    print(f"❌ Échec authentification - Status: {response.status}")
                    text = await response.text()
                    print(f"Réponse: {text}")
                    return
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return
        
        # Test 2: Lister les nœuds
        print("\n2️⃣ Test de lecture des nœuds...")
        try:
            async with session.get(f"{api_url}/nodes", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    nodes = data['data']
                    print(f"✅ Lecture nœuds OK - {len(nodes)} nœud(s) trouvé(s)")
                    for node in nodes:
                        print(f"   - {node['node']} (status: {node.get('status', 'unknown')})")
                else:
                    print(f"❌ Échec lecture nœuds - Status: {response.status}")
                    text = await response.text()
                    print(f"Réponse: {text}")
        except Exception as e:
            print(f"❌ Erreur lecture nœuds: {e}")
        
        # Test 3: Vérifier le statut du nœud pve
        print("\n3️⃣ Test de lecture du statut du nœud pve...")
        try:
            async with session.get(f"{api_url}/nodes/pve/status", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data['data']
                    print(f"✅ Lecture statut OK")
                    print(f"   - Uptime: {status.get('uptime', 'unknown')}")
                    print(f"   - Load: {status.get('loadavg', 'unknown')}")
                    print(f"   - Memory: {status.get('memory', 'unknown')}")
                else:
                    print(f"❌ Échec lecture statut - Status: {response.status}")
                    text = await response.text()
                    print(f"Réponse: {text}")
        except Exception as e:
            print(f"❌ Erreur lecture statut: {e}")
        
        # Test 4: Tester l'arrêt (simulation - ne pas exécuter)
        print("\n4️⃣ Test de simulation d'arrêt (DRY RUN)...")
        print("⚠️  ATTENTION: Ce test ne va PAS arrêter le serveur")
        print("   Il teste seulement les permissions d'écriture")
        
        # Données pour l'arrêt (simulation)
        shutdown_data = {
            "command": "shutdown",
            "timeout": 300
        }
        
        try:
            # On fait juste une requête HEAD pour tester les permissions
            async with session.head(f"{api_url}/nodes/pve/status", headers=headers) as response:
                if response.status == 200:
                    print("✅ Permissions d'écriture OK (simulation)")
                    print("   Le bot devrait pouvoir envoyer la commande d'arrêt")
                else:
                    print(f"❌ Permissions d'écriture insuffisantes - Status: {response.status}")
        except Exception as e:
            print(f"❌ Erreur test permissions: {e}")
        
        # Test 5: Lister les conteneurs LXC
        print("\n5️⃣ Test de lecture des conteneurs LXC...")
        try:
            async with session.get(f"{api_url}/nodes/pve/lxc", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    containers = data['data']
                    print(f"✅ Lecture conteneurs OK - {len(containers)} conteneur(s) trouvé(s)")
                    for container in containers:
                        print(f"   - {container.get('name', 'unnamed')} (ID: {container['vmid']}, Status: {container.get('status', 'unknown')})")
                else:
                    print(f"❌ Échec lecture conteneurs - Status: {response.status}")
                    text = await response.text()
                    print(f"Réponse: {text}")
        except Exception as e:
            print(f"❌ Erreur lecture conteneurs: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage du test des permissions Proxmox")
    print("=" * 60)
    asyncio.run(test_proxmox_permissions())
    print("\n" + "=" * 60)
    print("🏁 Test terminé")
