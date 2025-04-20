from langfuse import Langfuse
from langfuse.client import PromptClient
from .secret_manager import get_secret

_langfuse = None

def get_langfuse() -> Langfuse:
    global _langfuse
    if _langfuse is None:
        _langfuse = Langfuse(
            secret_key=get_secret("langfuse-secret"),
            public_key=get_secret("langfuse-pub"),
            host="https://cloud.langfuse.com")
    return _langfuse


def get_crypto_prompt() -> PromptClient:
    return get_langfuse().get_prompt("crypto")