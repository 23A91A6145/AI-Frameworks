from langchain_core.language_models import BaseChatModel

from config.settings import settings


def get_llm(provider: str | None = None) -> BaseChatModel:
    provider = provider or settings.provider
    api_key = settings.api_key

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.model_name,
            base_url=settings.ollama_base_url,
            temperature=settings.temperature,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.model_name,
            api_key=api_key,
            temperature=settings.temperature,
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        kwargs = {
            "model": settings.model_name,
            "api_key": api_key,
            "temperature": settings.temperature,
        }
        if settings.api_base_url:
            kwargs["base_url"] = settings.api_base_url
        return ChatOpenAI(**kwargs)

    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=api_key,
            temperature=settings.temperature,
        )

    elif provider == "mistral":
        from langchain_mistralai import ChatMistralAI

        return ChatMistralAI(
            model=settings.model_name,
            api_key=api_key,
            temperature=settings.temperature,
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}")
