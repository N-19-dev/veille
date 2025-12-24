# llm_provider.py
# Abstraction pour providers LLM interchangeables (Groq, OpenAI, Ollama)
#
# Objectif :
# - Éliminer la dépendance 100% Groq (risque mortel)
# - Permettre de switcher facilement de provider via config.yaml
# - Support 3 providers : Groq (gratuit), OpenAI (fallback), Ollama (local)

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from openai import OpenAI


# ==========================
#   Interface ABC
# ==========================

class LLMProvider(ABC):
    """Interface abstraite pour providers LLM interchangeables."""

    def __init__(self, model: str, temperature: float = 0.2):
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Appel générique de chat completion.

        Args:
            messages: Liste de messages [{"role": "system/user/assistant", "content": "..."}]
            temperature: Temperature pour la génération (override self.temperature si fourni)
            max_tokens: Nombre max de tokens dans la réponse
            response_format: Format de réponse (ex: {"type": "json_object"} pour JSON)

        Returns:
            str: Contenu de la réponse du LLM (brut : JSON string ou Markdown)

        Raises:
            Exception: Si l'appel API échoue
        """
        pass


# ==========================
#   Groq Provider (actuel)
# ==========================

class GroqProvider(LLMProvider):
    """Provider Groq (gratuit, rapide, actuel)."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.2,
        base_url: str = "https://api.groq.com/openai/v1"
    ):
        super().__init__(model, temperature)
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        temp = temperature if temperature is not None else self.temperature

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        if response_format is not None:
            kwargs["response_format"] = response_format

        resp = self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""


# ==========================
#   OpenAI Provider (fallback)
# ==========================

class OpenAIProvider(LLMProvider):
    """Provider OpenAI (fallback si Groq down, payant)."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        base_url: str = "https://api.openai.com/v1"
    ):
        super().__init__(model, temperature)
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        temp = temperature if temperature is not None else self.temperature

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        if response_format is not None:
            kwargs["response_format"] = response_format

        resp = self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""


# ==========================
#   Ollama Provider (local, gratuit)
# ==========================

class OllamaProvider(LLMProvider):
    """Provider Ollama (local, zéro coût, nécessite installation)."""

    def __init__(
        self,
        model: str = "llama3.1",
        temperature: float = 0.2,
        base_url: str = "http://localhost:11434/v1"
    ):
        super().__init__(model, temperature)
        # Ollama expose une API compatible OpenAI sur /v1
        # La clé API est dummy (Ollama ne l'utilise pas)
        self.client = OpenAI(base_url=base_url, api_key="ollama")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        temp = temperature if temperature is not None else self.temperature

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        # Note: Ollama peut ne pas supporter response_format JSON
        # On l'ajoute quand même, cela sera ignoré si non supporté
        if response_format is not None:
            kwargs["response_format"] = response_format

        resp = self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""


# ==========================
#   Factory Function
# ==========================

def get_provider(config: Dict[str, Any]) -> LLMProvider:
    """
    Factory pour créer le bon provider depuis config.yaml.

    Args:
        config: Section 'llm' de config.yaml parsé

    Returns:
        LLMProvider instance configurée

    Raises:
        ValueError: Si provider inconnu ou config invalide
        RuntimeError: Si variable d'environnement API key manquante

    Example config.yaml:
        llm:
          provider: groq  # ou openai, ou ollama
          temperature: 0.2

          # Config Groq
          groq:
            api_key_env: GROQ_API_KEY
            model: llama-3.1-8b-instant
            base_url: https://api.groq.com/openai/v1  # optionnel

          # Config OpenAI
          openai:
            api_key_env: OPENAI_API_KEY
            model: gpt-4o-mini
            base_url: https://api.openai.com/v1  # optionnel

          # Config Ollama (local)
          ollama:
            model: llama3.1
            base_url: http://localhost:11434/v1  # optionnel
    """
    provider_name = config.get("provider", "groq")
    temperature = float(config.get("temperature", 0.2))

    if provider_name == "groq":
        groq_cfg = config.get("groq", {})
        api_key_env = groq_cfg.get("api_key_env", "GROQ_API_KEY")
        api_key = os.getenv(api_key_env)

        if not api_key:
            raise RuntimeError(
                f"Variable d'environnement {api_key_env} manquante. "
                f"Configurez GROQ_API_KEY dans .env"
            )

        model = groq_cfg.get("model", "llama-3.1-8b-instant")
        base_url = groq_cfg.get("base_url", "https://api.groq.com/openai/v1")

        return GroqProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            base_url=base_url
        )

    elif provider_name == "openai":
        openai_cfg = config.get("openai", {})
        api_key_env = openai_cfg.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.getenv(api_key_env)

        if not api_key:
            raise RuntimeError(
                f"Variable d'environnement {api_key_env} manquante. "
                f"Configurez OPENAI_API_KEY dans .env"
            )

        model = openai_cfg.get("model", "gpt-4o-mini")
        base_url = openai_cfg.get("base_url", "https://api.openai.com/v1")

        return OpenAIProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
            base_url=base_url
        )

    elif provider_name == "ollama":
        ollama_cfg = config.get("ollama", {})
        model = ollama_cfg.get("model", "llama3.1")
        base_url = ollama_cfg.get("base_url", "http://localhost:11434/v1")

        return OllamaProvider(
            model=model,
            temperature=temperature,
            base_url=base_url
        )

    else:
        raise ValueError(
            f"Provider LLM inconnu : '{provider_name}'. "
            f"Valeurs supportées : groq, openai, ollama"
        )
