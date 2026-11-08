"""Erreurs du module, toutes dérivées de FicheError, en français."""

from __future__ import annotations


class FicheError(Exception):
    """Base de toutes les erreurs du module."""


class InvalidCourse(FicheError):
    """Le cours d'entrée ne respecte pas le contrat v1 ou n'a pas de section exploitable."""


class UnknownGabarit(FicheError):
    """Identifiant de gabarit inconnu."""

    def __init__(self, gabarit: str, known: list[str]) -> None:
        super().__init__(f"gabarit inconnu : {gabarit} (connus : {', '.join(known)})")
        self.gabarit = gabarit


class ProviderError(FicheError):
    """Un fournisseur de modèle a échoué après les relances."""

    def __init__(self, provider: str, message: str, retryable: bool = False) -> None:
        super().__init__(f"{provider} : {message}")
        self.provider, self.retryable = provider, retryable
