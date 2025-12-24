# sentry_init.py
# Initialisation de Sentry pour monitoring d'erreurs en production

import os
import sentry_sdk
from dotenv import load_dotenv

load_dotenv()


def init_sentry(
    environment: str = "production",
    enable_tracing: bool = True,
    enable_profiling: bool = False
):
    """
    Initialise Sentry pour le monitoring d'erreurs.

    Args:
        environment: "production", "development", ou "staging"
        enable_tracing: Active le tracing des performances
        enable_profiling: Active le profiling (CPU, mémoire)

    Note:
        Nécessite SENTRY_DSN_BACKEND dans .env
        Pour obtenir le DSN:
        1. Créer un compte sur https://sentry.io (gratuit)
        2. Créer un projet Python
        3. Copier le DSN depuis Settings → Client Keys
    """
    dsn = os.getenv("SENTRY_DSN_BACKEND")

    if not dsn:
        print("[warn] SENTRY_DSN_BACKEND manquant, monitoring désactivé")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,

        # Capture 100% des traces de performance (ajuster si trop coûteux)
        traces_sample_rate=1.0 if enable_tracing else 0.0,

        # Profiling (optionnel, utile pour optimiser perf)
        profiles_sample_rate=1.0 if enable_profiling else 0.0,

        # Ignorer certaines erreurs connues/bénignes
        ignore_errors=[
            KeyboardInterrupt,  # Ctrl+C normal
        ],

        # Capturer les variables locales (utile pour debug, attention données sensibles)
        attach_stacktrace=True,
        send_default_pii=False,  # Ne pas envoyer de données personnelles par défaut

        # Release tracking (optionnel, pour associer erreurs à une version)
        # release=os.getenv("SENTRY_RELEASE", "dev"),
    )

    print(f"[info] Sentry initialisé (env={environment})")


def set_context(context_type: str, **kwargs):
    """
    Ajoute du contexte custom aux erreurs Sentry.

    Exemple:
        set_context("pipeline", step="crawl", week_offset=-1)
        # Si erreur, Sentry affichera: pipeline.step=crawl, pipeline.week_offset=-1
    """
    sentry_sdk.set_context(context_type, kwargs)


def set_tag(key: str, value: str):
    """
    Ajoute un tag aux erreurs Sentry.

    Exemple:
        set_tag("source", "databricks-blog")
        # Permet de filtrer : "Toutes les erreurs source=databricks-blog"
    """
    sentry_sdk.set_tag(key, value)


def capture_exception(exception: Exception, **extra_data):
    """
    Capture manuellement une exception vers Sentry.

    Exemple:
        try:
            risky_operation()
        except ValueError as e:
            capture_exception(e, article_url="https://...", category="tech")
    """
    if extra_data:
        sentry_sdk.set_context("extra_data", extra_data)
    sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", **extra_data):
    """
    Envoie un message custom à Sentry (pas une erreur).

    Niveaux: "debug", "info", "warning", "error", "fatal"

    Exemple:
        capture_message("Feed Databricks down depuis 3 jours", level="warning")
    """
    if extra_data:
        sentry_sdk.set_context("extra_data", extra_data)
    sentry_sdk.capture_message(message, level=level)
