#!/usr/bin/env python3
"""
Test réel de l'API d'arrêt Proxmox
ATTENTION: Ce script va VRAIMENT arrêter le serveur !
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_real_shutdown():
    """Test réel de l'arrêt Proxmox"""
    
    # Configuration du bot
    api_url = "https://192.168.1.245:8006/api2/json"
    token_id = "cubeguardian@pam!cubeguardian-discord-bot"
    token_secret = "7420cec7-e4bc-4248-adc0-9c38738acce8"
    
    headers = {
        "Authorization": f"PVEAPIToken={token_id}={token_secret}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print("🔧 Test RÉEL de l'API d'arrêt Proxmox")
    print("⚠️  ATTENTION: Ce test va VRAIMENT arrêter le serveur !")
    print("=" * 60)
    
    # Confirmation de sécurité
    print("Voulez-vous vraiment arrêter le serveur Proxmox ?")
    print("Tapez 'OUI' pour confirmer (en majuscules):")
    confirmation = input("> ")
    
    if confirmation != "OUI":
        print("❌ Test annulé par l'utilisateur")
        return
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:
        
        # Test d'authentification
        print("\n1️⃣ Vérification de l'authentification...")
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
        
        # Envoi de la commande d'arrêt
        print("\n2️⃣ Envoi de la commande d'arrêt...")
        
        shutdown_url = f"{api_url}/nodes/pve/status"
        shutdown_data = {
            "command": "shutdown",
            "timeout": 300  # 5 minutes pour arrêt propre
        }
        
        try:
            async with session.post(shutdown_url, headers=headers, data=shutdown_data) as response:
                print(f"Status HTTP: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Commande d'arrêt envoyée avec succès !")
                    print(f"Réponse: {data}")
                    print("🔄 Le serveur devrait s'arrêter dans les 5 minutes")
                else:
                    print(f"❌ Échec de l'arrêt - Status: {response.status}")
                    text = await response.text()
                    print(f"Réponse: {text}")
                    
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi: {e}")

if __name__ == "__main__":
    print("🚀 Test RÉEL de l'API d'arrêt Proxmox")
    print("=" * 60)
    asyncio.run(test_real_shutdown())
    print("\n" + "=" * 60)
    print("🏁 Test terminé")
