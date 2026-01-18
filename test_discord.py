#!/usr/bin/env python3
"""
Test de connexion Discord pour Bot CubeGuardian
"""

import sys
import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Ajouter src au path
sys.path.insert(0, 'src')

# Charger les variables d'environnement
load_dotenv()

async def test_discord_connection():
    """Test de connexion Discord"""
    print('🧪 Test de connexion Discord...')
    
    # Configuration du bot
    intents = discord.Intents.default()
    intents.voice_states = True
    intents.members = True
    intents.guilds = True
    intents.messages = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'✅ Bot connecté en tant que {bot.user}')
        if bot.guilds:
            print(f'✅ Serveur Discord: {bot.guilds[0].name}')
            print(f'✅ Nombre de serveurs: {len(bot.guilds)}')
        else:
            print('⚠️ Aucun serveur trouvé')
        await bot.close()
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        print(f'❌ Erreur Discord: {event}')
        await bot.close()
    
    try:
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print('❌ Token Discord non trouvé')
            return
        
        print('🔄 Tentative de connexion...')
        await bot.start(token)
        
    except Exception as e:
        print(f'❌ Erreur de connexion: {e}')

if __name__ == "__main__":
    asyncio.run(test_discord_connection())
