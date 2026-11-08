"""Réglages du module, lus dans l'environnement (préfixe FICHE_) ou un fichier .env.

Chaque réglage porte sa raison d'être. `.env.example` est généré depuis ce modèle
(`fiche config-example`) : un test vérifie qu'il est à jour. Les clés des fournisseurs
(MISTRAL_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, AZURE_OPENAI_*) restent dans l'environnement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Provider = Literal["mistral", "openai", "azure", "anthropic", "fake"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FICHE_", env_file=".env", extra="ignore", use_attribute_docstrings=True
    )

    @field_validator("llm_provider", "judge_provider", mode="before")
    @classmethod
    def _lowercase(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    # --- Modèle de rédaction (plan de la fiche, blocs de chaque section)
    llm_provider: Provider = "mistral"
    """Fournisseur du modèle qui rédige. Mistral Large pour commencer : le moins cher des grands
    modèles, hébergé en Europe. À comparer avec GPT-6.1 Sol sur deux cas avant de trancher."""
    llm_model: str | None = None
    """Nom du modèle, ou du déploiement pour Azure. Vide : défaut du fournisseur."""
    llm_max_tokens: int = 8000
    """Longueur maximale d'une réponse. Les blocs d'une section tiennent en 3 000 jetons."""
    llm_concurrency: int = 4
    """Sections rédigées de front."""

    # --- Modèle de vérification (fidélité des blocs à leurs passages)
    verify: bool = True
    """Relire chaque bloc avec ses passages par un petit modèle ; un bloc non soutenu est retiré
    de la fiche et journalisé. False pour mesurer le rédacteur seul."""
    judge_provider: Provider = "mistral"
    """Fournisseur du modèle vérificateur."""
    judge_model: str | None = "mistral-small-latest"
    """Petit modèle : la question est fermée (soutenu ou non), le coût doit rester marginal."""

    # --- Budget par document, vérifié avant chaque appel
    max_cost_usd: float = 0.50
    """Plafond de dépense par fiche, en dollars, d'après la table des prix de Pydantic AI.
    Atteint : les sections restantes sortent en « budget » et la fiche est publiée sans elles."""
    unknown_cost_usd: float = 0.02
    """Coût compté pour un appel dont le modèle n'est pas dans la table des prix."""

    # --- Gabarits
    gabarits_dir: Path | None = None
    """Dossier de gabarits YAML à la place de ceux du module (pour en essayer de nouveaux)."""

    # --- Cache et sorties
    cache_dir: Path = Path(".fiche_cache")
    """Cache disque des appels : rejouer une fiche ne repaie rien."""
    cache_enabled: bool = True
    """False pour mesurer la variabilité du modèle."""


KEYS_HEADER = """# Copier en .env et renseigner. Généré par `fiche config-example` depuis src/fiche/config.py :
# chaque réglage FICHE_* y est documenté, avec sa valeur par défaut.

# --- Clés des fournisseurs (jamais dans un commit)
MISTRAL_API_KEY=                            # rédacteur et vérificateur par défaut
# OPENAI_API_KEY=                           # FICHE_LLM_PROVIDER=openai
# ANTHROPIC_API_KEY=                        # FICHE_LLM_PROVIDER=anthropic
# AZURE_OPENAI_ENDPOINT=                    # FICHE_LLM_PROVIDER=azure, avec AZURE_OPENAI_API_KEY,
# AZURE_OPENAI_API_KEY=                     # AZURE_OPENAI_DEPLOYMENT et AZURE_OPENAI_API_VERSION
"""

_GROUPS = {
    "llm_provider": "Modèle de rédaction",
    "verify": "Vérification",
    "max_cost_usd": "Budget par document",
    "gabarits_dir": "Gabarits",
    "cache_dir": "Cache",
}


def env_example() -> str:
    """Le contenu de .env.example : les clés, puis chaque réglage avec sa documentation."""
    lines = [KEYS_HEADER]
    section = None
    for name, field in Settings.model_fields.items():
        group = _GROUPS.get(name)
        if group and group != section:
            section = group
            lines.append(f"\n# --- {section}")
        default = field.default
        if isinstance(default, bool):
            shown = str(default).lower()
        elif default is None:
            shown = ""
        elif isinstance(default, Path):
            shown = default.as_posix()
        else:
            shown = str(default)
        doc = " ".join((field.description or "").split())
        lines.append(f"# {doc}")
        lines.append(f"# FICHE_{name.upper()}={shown}")
    return "\n".join(lines) + "\n"


def get_settings() -> Settings:
    from dotenv import load_dotenv

    load_dotenv(".env", override=False)
    return Settings()
