"""Les gabarits de filière : une recette versionnée par famille, en YAML.

Un gabarit dit quels blocs la fiche peut utiliser et pour quoi, dans quel ordre les présenter,
combien par section, sur quel ton, et ce que la filière regarde en premier. Il ne contient
aucun exemple tiré d'un cours : c'est une consigne, pas un modèle à recopier.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from fiche.errors import UnknownGabarit
from fiche.models import BLOCK_KINDS

BUILTIN_DIR = Path(__file__).parent / "familles"


class BlocUsage(BaseModel):
    type: str
    usage: str = Field(description="Quand et pour quoi produire ce bloc, dans cette filière")

    @field_validator("type")
    @classmethod
    def _known(cls, value: str) -> str:
        if value not in BLOCK_KINDS:
            raise ValueError(f"type de bloc inconnu : {value}")
        return value


class Gabarit(BaseModel):
    id: str
    version: int = 1
    nom: str
    filieres: list[str]
    pour_etudiant: str = Field(description="Ce que l'étudiant lit pour choisir ce gabarit")
    ton: str
    blocs: list[BlocUsage]
    ordre: list[str] = Field(description="Ordre conseillé des types de blocs dans une section")
    max_blocs_par_section: int = 7
    max_texte_par_section: int = 1
    fin_de_chapitre: list[str] = Field(
        default_factory=lambda: ["essentiel", "autotest"],
        description="Blocs réservés à la dernière unité de chaque chapitre, et obligatoires là",
    )
    voix: str = Field(
        default="", description="Comment on écrit dans cette filière, en plus de la charte"
    )
    plan: str = Field(description="Consignes pour l'appel plan : ce que la fiche doit faire voir")
    redaction: str = Field(
        description="Consignes pour l'appel blocs : comment remplir chaque forme"
    )

    @model_validator(mode="after")
    def _coherent(self) -> Gabarit:
        allowed = self.allowed()
        unknown = [t for t in self.ordre if t not in allowed]
        if unknown:
            raise ValueError(f"{self.id} : ordre cite des blocs non autorisés : {unknown}")
        outside = [t for t in self.fin_de_chapitre if t not in allowed]
        if outside:
            raise ValueError(
                f"{self.id} : fin_de_chapitre cite des blocs non autorisés : {outside}"
            )
        if len(set(allowed)) != len(allowed):
            raise ValueError(f"{self.id} : un type de bloc est répété")
        return self

    def allowed(self) -> list[str]:
        return [b.type for b in self.blocs]

    def rank(self, kind: str) -> int:
        return self.ordre.index(kind) if kind in self.ordre else len(self.ordre)


def load_gabarits(directory: Path | None = None) -> dict[str, Gabarit]:
    """Tous les gabarits d'un dossier (ceux du module par défaut), par identifiant."""
    out: dict[str, Gabarit] = {}
    for path in sorted((directory or BUILTIN_DIR).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        gabarit = Gabarit.model_validate(data)
        if gabarit.id in out:
            raise ValueError(f"gabarit {gabarit.id} défini deux fois")
        out[gabarit.id] = gabarit
    return out


def get_gabarit(gabarit_id: str, directory: Path | None = None) -> Gabarit:
    gabarits = load_gabarits(directory)
    if gabarit_id not in gabarits:
        raise UnknownGabarit(gabarit_id, sorted(gabarits))
    return gabarits[gabarit_id]
