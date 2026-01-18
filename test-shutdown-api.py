#!/usr/bin/env python3
"""
Test direct de l'API d'arrêt Proxmox
ATTENTION: Ce script peut arrêter le serveur !
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_shutdown_api(dry_run=True):
    """
    Test de l'API d'arrêt Proxmox
    
    Args:
        dry_run: Si True, ne fait que simuler (ne pas arrêter)
    """
    
    # Configuration du bot
    api_url = "https://192.168.1.245:8006/api2/json"
    token_id = "cubeguardian@pam!cubeguardian-discord-bot"
    token_secret = "7420cec7-e4bc-4248-adc0-9c38738acce8"
    
    headers = {
        "Authorization": f"PVEAPIToken={token_id}={token_secret}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print("🔧 Test de l'API d'arrêt Proxmox")
    print(f"API URL: {api_url}")
    print(f"Token ID: {token_id}")
    print(f"Mode: {'DRY RUN (simulation)' if dry_run else 'EXÉCUTION RÉELLE'}")
    print("-" * 50)
    
    if not dry_run:
        print("⚠️  ATTENTION: Ce test va VRAIMENT arrêter le serveur !")
        print("⚠️  Assurez-vous que c'est ce que vous voulez faire !")
        response = input("Tapez 'CONFIRMER' pour continuer: ")
        if response != "CONFIRMER":
            print("❌ Test annulé par l'utilisateur")
            return
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:
        
        # Test 1: Vérifier l'authentification
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
        
        # Test 2: Vérifier le statut actuel du nœud
        print("\n2️⃣ Vérification du statut actuel du nœud...")
        try:
            async with session.get(f"{api_url}/nodes/pve/status", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data['data']
                    print(f"✅ Statut nœud OK")
                    print(f"   - Uptime: {status.get('uptime', 'unknown')} secondes")
                    print(f"   - Load: {status.get('loadavg', 'unknown')}")
                    print(f"   - Memory: {status.get('memory', 'unknown')}")
                else:
                    print(f"❌ Échec lecture statut - Status: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Erreur lecture statut: {e}")
            return
        
        # Test 3: Préparer la commande d'arrêt
        print("\n3️⃣ Préparation de la commande d'arrêt...")
        
        shutdown_url = f"{api_url}/nodes/pve/status"
        shutdown_data = {
            "command": "shutdown",
            "timeout": 300  # 5 minutes pour arrêt propre
        }
        
        print(f"URL: {shutdown_url}")
        print(f"Données: {shutdown_data}")
        
        if dry_run:
            print("✅ Commande d'arrêt préparée (simulation)")
            print("   En mode DRY RUN, la commande ne sera pas envoyée")
            print("   Pour exécuter réellement, relancez avec dry_run=False")
        else:
            # Test 4: Envoyer la commande d'arrêt
            print("\n4️⃣ Envoi de la commande d'arrêt...")
            try:
                async with session.post(shutdown_url, headers=headers, data=shutdown_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Commande d'arrêt envoyée avec succès")
                        print(f"Réponse: {data}")
                        print("🔄 Le serveur devrait s'arrêter dans les 5 minutes")
                    else:
                        print(f"❌ Échec envoi commande d'arrêt - Status: {response.status}")
                        text = await response.text()
                        print(f"Réponse: {text}")
            except Exception as e:
                print(f"❌ Erreur envoi commande: {e}")

async def test_simple_shutdown():
    """Test simple de l'arrêt (version simplifiée)"""
    
    print("🔧 Test simple de l'API d'arrêt")
    print("=" * 40)
    
    # Configuration
    api_url = "https://192.168.1.245:8006/api2/json"
    token_id = "cubeguardian@pam!cubeguardian-discord-bot"
    token_secret = "7420cec7-e4bc-4248-adc0-9c38738acce8"
    
    headers = {
        "Authorization": f"PVEAPIToken={token_id}={token_secret}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Données pour l'arrêt
    data = "command=shutdown&timeout=300"
    
    print(f"URL: {api_url}/nodes/pve/status")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    print("\n⚠️  Cette commande va arrêter le serveur !")
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:
        try:
            async with session.post(
                f"{api_url}/nodes/pve/status", 
                headers=headers, 
                data=data
            ) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Test de l'API d'arrêt Proxmox")
    print("=" * 50)
    
    # Mode par défaut: simulation
    print("Mode par défaut: DRY RUN (simulation)")
    print("Pour exécuter réellement, modifiez dry_run=False dans le code")
    print()
    
    asyncio.run(test_shutdown_api(dry_run=True))
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")
    print("\nPour tester l'arrêt réel:")
    print("1. Modifiez le token_secret dans le script")
    print("2. Changez dry_run=False")
    print("3. Relancez le script")
