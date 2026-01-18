#!/usr/bin/env python3
"""
Test corrigé de l'API d'arrêt Proxmox
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_fixed_shutdown():
    """Test corrigé de l'arrêt Proxmox"""
    
    # Configuration du bot
    api_url = "https://192.168.1.245:8006/api2/json"
    token_id = "cubeguardian@pam!cubeguardian-discord-bot"
    token_secret = "7420cec7-e4bc-4248-adc0-9c38738acce8"
    
    headers = {
        "Authorization": f"PVEAPIToken={token_id}={token_secret}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print("🔧 Test CORRIGÉ de l'API d'arrêt Proxmox")
    print("=" * 50)
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:
        
        # Test d'authentification
        print("1️⃣ Vérification de l'authentification...")
        try:
            async with session.get(f"{api_url}/version", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Authentification OK - Version: {data['data']['version']}")
                else:
                    print(f"❌ Échec authentification - Status: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return
        
        # Test 1: Arrêt sans timeout
        print("\n2️⃣ Test 1: Arrêt sans paramètre timeout...")
        shutdown_url = f"{api_url}/nodes/pve/status"
        data1 = "command=shutdown"
        
        try:
            async with session.post(shutdown_url, headers=headers, data=data1) as response:
                print(f"Status HTTP: {response.status}")
                text = await response.text()
                print(f"Réponse: {text}")
                
                if response.status == 200:
                    print("✅ Arrêt sans timeout réussi !")
                else:
                    print("❌ Échec de l'arrêt sans timeout")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test 2: Arrêt avec timeout (format correct)
        print("\n3️⃣ Test 2: Arrêt avec timeout (format correct)...")
        data2 = "command=shutdown&timeout=300"
        
        try:
            async with session.post(shutdown_url, headers=headers, data=data2) as response:
                print(f"Status HTTP: {response.status}")
                text = await response.text()
                print(f"Réponse: {text}")
                
                if response.status == 200:
                    print("✅ Arrêt avec timeout réussi !")
                else:
                    print("❌ Échec de l'arrêt avec timeout")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test 3: Vérifier les paramètres acceptés
        print("\n4️⃣ Test 3: Vérification des paramètres acceptés...")
        try:
            # Essayer de récupérer le schéma de l'API
            schema_url = f"{api_url}/nodes/pve/status"
            async with session.get(schema_url, headers=headers) as response:
                print(f"Status GET: {response.status}")
                if response.status == 200:
                    text = await response.text()
                    print(f"Réponse GET: {text}")
        except Exception as e:
            print(f"❌ Erreur GET: {e}")

if __name__ == "__main__":
    print("🚀 Test CORRIGÉ de l'API d'arrêt Proxmox")
    print("=" * 50)
    asyncio.run(test_fixed_shutdown())
    print("\n" + "=" * 50)
    print("🏁 Test terminé")
