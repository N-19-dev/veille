# test_llm_provider.py
# Tests unitaires pour l'abstraction LLM provider

import pytest
import os
from unittest.mock import patch, MagicMock

from llm_provider import (
    get_provider,
    GroqProvider,
    OpenAIProvider,
    OllamaProvider,
    LLMProvider
)


# ==========================
#   Tests get_provider()
# ==========================

def test_get_provider_groq():
    """Test création provider Groq depuis config."""
    config = {
        "provider": "groq",
        "temperature": 0.2,
        "groq": {
            "api_key_env": "GROQ_API_KEY",
            "model": "llama-3.1-8b-instant",
            "base_url": "https://api.groq.com/openai/v1"
        }
    }

    with patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key"}):
        provider = get_provider(config)

        assert isinstance(provider, GroqProvider)
        assert provider.model == "llama-3.1-8b-instant"
        assert provider.temperature == 0.2


def test_get_provider_openai():
    """Test création provider OpenAI depuis config."""
    config = {
        "provider": "openai",
        "temperature": 0.3,
        "openai": {
            "api_key_env": "OPENAI_API_KEY",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1"
        }
    }

    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-openai-key"}):
        provider = get_provider(config)

        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4o-mini"
        assert provider.temperature == 0.3


def test_get_provider_ollama():
    """Test création provider Ollama depuis config."""
    config = {
        "provider": "ollama",
        "temperature": 0.1,
        "ollama": {
            "model": "llama3.1",
            "base_url": "http://localhost:11434/v1"
        }
    }

    provider = get_provider(config)

    assert isinstance(provider, OllamaProvider)
    assert provider.model == "llama3.1"
    assert provider.temperature == 0.1


def test_get_provider_unknown():
    """Test erreur si provider inconnu."""
    config = {
        "provider": "unknown_provider",
        "temperature": 0.2
    }

    with pytest.raises(ValueError, match="Provider LLM inconnu"):
        get_provider(config)


def test_get_provider_missing_groq_api_key():
    """Test erreur si GROQ_API_KEY manquante."""
    config = {
        "provider": "groq",
        "groq": {
            "api_key_env": "GROQ_API_KEY",
            "model": "llama-3.1-8b-instant"
        }
    }

    # S'assurer que la variable n'existe pas
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="GROQ_API_KEY manquante"):
            get_provider(config)


def test_get_provider_missing_openai_api_key():
    """Test erreur si OPENAI_API_KEY manquante."""
    config = {
        "provider": "openai",
        "openai": {
            "api_key_env": "OPENAI_API_KEY",
            "model": "gpt-4o-mini"
        }
    }

    # S'assurer que la variable n'existe pas
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY manquante"):
            get_provider(config)


# ==========================
#   Tests chat_completion()
# ==========================

def test_groq_provider_chat_completion():
    """Test chat_completion avec GroqProvider (mocked)."""
    with patch.dict(os.environ, {"GROQ_API_KEY": "fake-key"}):
        provider = GroqProvider(api_key="fake-key", model="llama-3.1-8b-instant")

        # Mock le client OpenAI
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"

        with patch.object(provider.client.chat.completions, 'create', return_value=mock_response):
            result = provider.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.0
            )

            assert result == "Test response"
            provider.client.chat.completions.create.assert_called_once()


def test_openai_provider_chat_completion():
    """Test chat_completion avec OpenAIProvider (mocked)."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"}):
        provider = OpenAIProvider(api_key="fake-key", model="gpt-4o-mini")

        # Mock le client OpenAI
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "OpenAI response"

        with patch.object(provider.client.chat.completions, 'create', return_value=mock_response):
            result = provider.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.5,
                max_tokens=100
            )

            assert result == "OpenAI response"
            provider.client.chat.completions.create.assert_called_once()


def test_ollama_provider_chat_completion():
    """Test chat_completion avec OllamaProvider (mocked)."""
    provider = OllamaProvider(model="llama3.1")

    # Mock le client OpenAI
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Ollama response"

    with patch.object(provider.client.chat.completions, 'create', return_value=mock_response):
        result = provider.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            response_format={"type": "json_object"}
        )

        assert result == "Ollama response"
        provider.client.chat.completions.create.assert_called_once()


def test_provider_temperature_override():
    """Test override de temperature dans chat_completion."""
    with patch.dict(os.environ, {"GROQ_API_KEY": "fake-key"}):
        provider = GroqProvider(api_key="fake-key", model="llama-3.1-8b-instant", temperature=0.2)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test"

        with patch.object(provider.client.chat.completions, 'create', return_value=mock_response) as mock_create:
            provider.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.9  # Override
            )

            # Vérifier que temperature=0.9 a été passée (pas 0.2)
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["temperature"] == 0.9


# ==========================
#   Tests Configuration Defaults
# ==========================

def test_groq_provider_defaults():
    """Test valeurs par défaut GroqProvider."""
    with patch.dict(os.environ, {"GROQ_API_KEY": "fake-key"}):
        provider = GroqProvider(api_key="fake-key")

        assert provider.model == "llama-3.1-8b-instant"
        assert provider.temperature == 0.2


def test_openai_provider_defaults():
    """Test valeurs par défaut OpenAIProvider."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"}):
        provider = OpenAIProvider(api_key="fake-key")

        assert provider.model == "gpt-4o-mini"
        assert provider.temperature == 0.2


def test_ollama_provider_defaults():
    """Test valeurs par défaut OllamaProvider."""
    provider = OllamaProvider()

    assert provider.model == "llama3.1"
    assert provider.temperature == 0.2


# ==========================
#   Tests Interface ABC
# ==========================

def test_llm_provider_is_abstract():
    """Test que LLMProvider est abstraite et ne peut pas être instanciée directement."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        LLMProvider(model="test", temperature=0.2)
