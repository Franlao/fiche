"""fiche : d'un cours structuré (contrat v1 d'ingest) à une fiche de révision en blocs typés.

Porte d'entrée : `run(FicheRequest) -> Fiche`. Voir README.md.
"""

from fiche.models import Fiche
from fiche.request import FicheRequest
from fiche.run import run

__all__ = ["Fiche", "FicheRequest", "run"]
