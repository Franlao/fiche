"""La requête : ce qu'on donne au module."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from fiche.config import Settings


class FicheRequest(BaseModel):
    """Le cours (résultat v1 d'ingest en JSON) et les options. Les options absentes gardent
    la valeur des réglages."""

    course: Path
    gabarit: str | None = None
    """Identifiant du gabarit. Vide : suggéré par un appel court, à confirmer par l'étudiant."""
    llm: str | None = None
    """`fournisseur:modèle` du rédacteur, par exemple `openai:gpt-6.1-sol`."""
    verify: bool | None = None
    max_cost_usd: float | None = None

    def settings(self, base: Settings) -> Settings:
        update: dict[str, object] = {}
        if self.llm is not None:
            provider, _, model = self.llm.partition(":")
            update["llm_provider"] = provider
            update["llm_model"] = model or None
        if self.verify is not None:
            update["verify"] = self.verify
        if self.max_cost_usd is not None:
            update["max_cost_usd"] = self.max_cost_usd
        return base.model_copy(update=update)
