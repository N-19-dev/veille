# logger.py
"""
Module de logging structuré pour le projet de veille technologique.
Permet un tracking détaillé des erreurs et métriques pour le monitoring.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

class StructuredLogger:
    """Logger avec support de logging structuré (JSON) pour faciliter le monitoring."""

    def __init__(self, name: str, log_file: Optional[str] = None, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()

        # Format structuré
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (optionnel)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str, **context):
        """Log niveau INFO avec contexte optionnel."""
        self._log(logging.INFO, message, context)

    def warning(self, message: str, **context):
        """Log niveau WARNING avec contexte optionnel."""
        self._log(logging.WARNING, message, context)

    def error(self, message: str, **context):
        """Log niveau ERROR avec contexte optionnel."""
        self._log(logging.ERROR, message, context)

    def debug(self, message: str, **context):
        """Log niveau DEBUG avec contexte optionnel."""
        self._log(logging.DEBUG, message, context)

    def _log(self, level: int, message: str, context: dict):
        """Méthode interne pour logger avec contexte."""
        if context:
            # Ajoute le contexte au message
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            full_message = f"{message} | {context_str}"
        else:
            full_message = message

        self.logger.log(level, full_message)


class MetricsCollector:
    """Collecteur de métriques pour monitoring."""

    def __init__(self):
        self.metrics = {
            "start_time": datetime.now().isoformat(),
            "feeds_processed": 0,
            "feeds_failed": 0,
            "articles_crawled": 0,
            "articles_filtered": 0,
            "articles_classified": 0,
            "llm_calls": 0,
            "errors": [],
        }

    def increment(self, key: str, value: int = 1):
        """Incrémenter une métrique."""
        if key in self.metrics:
            self.metrics[key] += value

    def add_error(self, error_type: str, message: str, url: Optional[str] = None):
        """Ajouter une erreur au tracking."""
        self.metrics["errors"].append({
            "type": error_type,
            "message": message,
            "url": url,
            "timestamp": datetime.now().isoformat()
        })

    def get_summary(self) -> dict:
        """Obtenir un résumé des métriques."""
        self.metrics["end_time"] = datetime.now().isoformat()
        return self.metrics

    def save(self, path: str):
        """Sauvegarder les métriques dans un fichier JSON."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.get_summary(), f, indent=2, ensure_ascii=False)


def get_logger(name: str, log_file: Optional[str] = None, level: str = "INFO") -> StructuredLogger:
    """Factory function pour créer un logger."""
    return StructuredLogger(name, log_file, level)
