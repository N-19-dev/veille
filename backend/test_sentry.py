#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration Sentry.
Lance une erreur volontaire et vérifie qu'elle est capturée par Sentry.
"""

import sys
import time
from sentry_init import init_sentry, capture_exception, capture_message, set_tag, set_context

def test_backend_sentry():
    print("🔍 Test de l'intégration Sentry Backend...")
    print("-" * 50)

    # Initialiser Sentry
    init_sentry(environment="development", enable_tracing=True)
    print("✅ Sentry initialisé (environment: development)")

    # Ajouter des tags pour identifier le test
    set_tag("test_type", "integration_test")
    set_tag("component", "sentry_verification")
    print("✅ Tags ajoutés")

    # Ajouter du contexte custom
    set_context("test_info",
        test_name="Backend Sentry Integration",
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        purpose="Verify error tracking works"
    )
    print("✅ Contexte ajouté")

    # Test 1: Capture d'un message informatif
    print("\n📝 Test 1: Capture d'un message...")
    capture_message("Test message from Sentry integration test", level="info")
    print("✅ Message envoyé à Sentry")

    # Test 2: Capture d'une exception
    print("\n💥 Test 2: Capture d'une exception...")
    try:
        # Erreur volontaire
        result = 1 / 0
    except ZeroDivisionError as e:
        capture_exception(e)
        print("✅ Exception capturée et envoyée à Sentry")

    print("\n" + "=" * 50)
    print("✨ Tests terminés !")
    print("=" * 50)
    print("\n📊 Vérification dans Sentry Dashboard:")
    print("1. Aller sur https://sentry.io")
    print("2. Sélectionner le projet 'veille-tech-backend'")
    print("3. Aller dans 'Issues'")
    print("4. Vous devriez voir:")
    print("   - Un message: 'Test message from Sentry integration test'")
    print("   - Une erreur: 'ZeroDivisionError: division by zero'")
    print("\n💡 Si vous voyez ces 2 entrées → Sentry fonctionne parfaitement ✅")
    print("❌ Si rien n'apparaît → Vérifier SENTRY_DSN_BACKEND dans .env")

    # Attendre un peu pour que Sentry envoie les données
    print("\n⏳ Attente de 2 secondes pour l'envoi des données...")
    time.sleep(2)
    print("✅ Terminé")

if __name__ == "__main__":
    test_backend_sentry()
