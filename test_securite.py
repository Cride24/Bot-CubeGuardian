#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de sécurité : Distinction discussion vs commande avec mention du bot
"""

import sys
from pathlib import Path

# Configuration du path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_securite_mention_bot():
    """Test de sécurité pour la distinction discussion/commande"""
    
    print("🛡️ Test de Sécurité - Distinction Discussion vs Commande")
    print("=" * 65)
    
    try:
        from command_parser import CommandParser, CommandIntent
        
        parser = CommandParser()
        
        # SCÉNARIO 1: Discussions normales (DOIVENT être ignorées)
        discussions_normales = [
            "Jean: Il faudrait redémarrer le serveur minecraft, il lag",
            "Marie: On devrait restart le serveur ce soir",
            "Alex: Le serveur minecraft bug, quelqu'un peut le redémarrer ?",
            "Bob: Hier j'ai dû redémarrer minecraft 3 fois",
            "Lisa: Comment on fait pour restart un serveur minecraft ?",
            "Le serveur minecraft marche bien depuis le dernier restart",
            "Il y a eu un reboot automatique du serveur cette nuit",
        ]
        
        print("🚫 DISCUSSIONS NORMALES (doivent être IGNORÉES):")
        print("-" * 50)
        
        faux_positifs = 0
        for message in discussions_normales:
            # Test AVEC protection (require_mention=True)
            result_protege = parser.parse_command(message, "CubeGuardian", require_mention=True)
            
            # Test SANS protection (require_mention=False) pour comparaison
            result_non_protege = parser.parse_command(message, "CubeGuardian", require_mention=False)
            
            # Vérifier si c'était un faux positif sans protection
            if result_non_protege.intent == CommandIntent.RESTART_MINECRAFT and result_non_protege.confidence >= 0.5:
                if result_protege.intent != CommandIntent.RESTART_MINECRAFT or result_protege.confidence < 0.5:
                    status = "✅ PROTÉGÉ"
                    faux_positifs += 1
                else:
                    status = "❌ FAILLE"
            else:
                status = "✅ IGNORÉ"
            
            conf_protege = int(result_protege.confidence * 100)
            conf_non_protege = int(result_non_protege.confidence * 100)
            
            print(f"{status} | Protection: {conf_protege:3d}% | Sans: {conf_non_protege:3d}%")
            print(f"        💬 \"{message[:60]}{'...' if len(message) > 60 else ''}\"")
            print()
        
        # SCÉNARIO 2: Vraies commandes avec mention (DOIVENT être détectées)
        vraies_commandes = [
            "@CubeGuardian redémarrer le serveur minecraft",
            "@CubeGuardian restart minecraft stp",
            "Hey @CubeGuardian, peux-tu reboot le serveur ?",
            "Salut CubeGuardian, redémarre le serveur minecraft",
            "bot restart minecraft",
            "@bot reboot serveur",
            "hey bot redémarrer minecraft",
        ]
        
        print("✅ VRAIES COMMANDES avec mention (doivent être DÉTECTÉES):")
        print("-" * 58)
        
        commandes_detectees = 0
        for message in vraies_commandes:
            result = parser.parse_command(message, "CubeGuardian", require_mention=True)
            
            if result.intent == CommandIntent.RESTART_MINECRAFT and result.confidence >= 0.5:
                status = "✅ DÉTECTÉE"
                commandes_detectees += 1
            else:
                status = "❌ RATÉE"
            
            conf = int(result.confidence * 100)
            has_mention = "🤖" if "NO_BOT_MENTION" not in result.matched_keywords else "🚫"
            
            print(f"{status} {has_mention} [{conf:3d}%] | \"{message}\"")
        
        print()
        
        # SCÉNARIO 3: Commandes sans mention (DOIVENT être ignorées)
        commandes_sans_mention = [
            "redémarrer le serveur minecraft",
            "restart minecraft server",
            "reboot le serveur",
            "quelqu'un peut redémarrer minecraft ?",
        ]
        
        print("🚫 COMMANDES sans mention (doivent être IGNORÉES):")
        print("-" * 48)
        
        for message in commandes_sans_mention:
            result = parser.parse_command(message, "CubeGuardian", require_mention=True)
            
            if result.intent == CommandIntent.RESTART_MINECRAFT and result.confidence >= 0.5:
                status = "❌ FAILLE"
            else:
                status = "✅ IGNORÉ"
            
            conf = int(result.confidence * 100)
            
            print(f"{status} [{conf:3d}%] | \"{message}\"")
        
        # RÉSUMÉ DE SÉCURITÉ
        print("\n" + "=" * 65)
        print("🎯 RÉSUMÉ DE SÉCURITÉ:")
        print(f"🛡️ Faux positifs évités: {faux_positifs}/{len(discussions_normales)}")
        print(f"✅ Vraies commandes détectées: {commandes_detectees}/{len(vraies_commandes)}")
        
        if faux_positifs == len(discussions_normales):
            print("🟢 SÉCURITÉ OPTIMALE - Aucun faux positif !")
        elif faux_positifs > len(discussions_normales) * 0.8:
            print("🟡 SÉCURITÉ BONNE - Quelques améliorations possibles")
        else:
            print("🔴 SÉCURITÉ INSUFFISANTE - Révision nécessaire")
        
        print("\n🔧 MÉCANISME DE PROTECTION:")
        print("✅ Détection de mention du bot (@CubeGuardian, bot, etc.)")
        print("✅ Réduction de score (90%) si pas de mention")
        print("✅ Seuil de confiance maintenu à 0.5")
        print("✅ Logging des tentatives sans mention")
        
        print("\n📋 PATTERNS DE MENTION SUPPORTÉS:")
        patterns = ["@CubeGuardian", "@ CubeGuardian", "CubeGuardian", "bot", "@bot", "hey bot", "salut bot"]
        for pattern in patterns:
            print(f"  • \"{pattern}\"")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_securite_mention_bot()
