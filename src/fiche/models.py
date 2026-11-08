"""Les blocs typés de la fiche, les sorties demandées au modèle, et la fiche assemblée.

Principe : le modèle remplit un schéma, l'application met en forme. Un bloc est une structure
(colonnes et lignes, étapes, cas, questions et réponses), jamais un texte libre à mettre en
page. Le bloc `texte` existe pour une transition ou une idée qui ne rentre dans aucune forme ;
les gabarits en limitent le nombre.

Chaque bloc cite les numéros des extraits (passages) qui le justifient, tels que montrés au
modèle ; l'assemblage les convertit en identifiants et en pages.
"""

from __future__ import annotations

from typing import Annotated, Literal, get_args

from pydantic import BaseModel, Field

BlockKind = Literal[
    "texte",
    "definition",
    "encadre",
    "tableau",
    "etapes",
    "frise",
    "decision",
    "exemple",
    "piege",
    "essentiel",
    "autotest",
]
BLOCK_KINDS: tuple[str, ...] = get_args(BlockKind)

BLOCK_LABELS: dict[str, str] = {
    "texte": "Texte court",
    "definition": "Définition",
    "encadre": "Encadré",
    "tableau": "Tableau",
    "etapes": "Étapes",
    "frise": "Frise",
    "decision": "Arbre de décision",
    "exemple": "Exemple résolu",
    "piege": "Pièges",
    "essentiel": "L'essentiel",
    "autotest": "Teste-toi",
}

Refs = Annotated[
    list[int],
    Field(
        description="Numéros des extraits qui justifient le bloc, tels que donnés entre crochets"
    ),
]


class TexteBloc(BaseModel):
    type: Literal["texte"]
    titre: str = Field(description="Titre court, ou vide")
    contenu: str = Field(description="2 à 4 phrases courtes, fidèles au cours")
    passages: Refs


class DefinitionBloc(BaseModel):
    type: Literal["definition"]
    titre: str = Field(description="Le terme défini, avec la notation du cours")
    definition: str = Field(description="La définition, 1 à 3 phrases, mots du cours")
    exemple: str = Field(description="Un exemple donné par le cours, ou vide")
    passages: Refs


class Variable(BaseModel):
    symbole: str
    signification: str


class EncadreBloc(BaseModel):
    """Ce qu'il faut savoir par cœur : théorème, propriété, formule, règle, loi, principe."""

    type: Literal["encadre"]
    nature: Literal["theoreme", "propriete", "formule", "regle", "loi", "principe"]
    titre: str = Field(description="Nom du résultat tel que le cours le nomme")
    enonce: str = Field(description="L'énoncé exact ; formules en LaTeX entre $ $")
    conditions: list[str] = Field(description="Hypothèses ou conditions de validité, ou liste vide")
    variables: list[Variable] = Field(description="Sens de chaque symbole de la formule, ou vide")
    idee: str = Field(
        description="Pourquoi c'est vrai, ou à quoi ça sert, si le cours le dit ; sinon vide"
    )
    passages: Refs


class TableauBloc(BaseModel):
    type: Literal["tableau"]
    titre: str
    colonnes: list[str] = Field(description="2 à 5 en-têtes de colonnes")
    lignes: list[list[str]] = Field(description="Chaque ligne a autant de cellules que de colonnes")
    passages: Refs


class Etape(BaseModel):
    titre: str = Field(description="3 à 8 mots")
    detail: str = Field(description="1 ou 2 phrases")


class EtapesBloc(BaseModel):
    """Un processus, un mécanisme, une méthode : dans l'ordre."""

    type: Literal["etapes"]
    titre: str
    etapes: list[Etape] = Field(description="2 à 8 étapes ordonnées")
    passages: Refs


class Evenement(BaseModel):
    repere: str = Field(description="Date, période ou rang")
    evenement: str


class FriseBloc(BaseModel):
    type: Literal["frise"]
    titre: str
    evenements: list[Evenement] = Field(description="3 à 10 repères ordonnés")
    passages: Refs


class Cas(BaseModel):
    si: str = Field(description="La condition ou la situation")
    alors: str = Field(description="Ce qui en découle selon le cours")


class DecisionBloc(BaseModel):
    """Quand le cours distingue des cas : « si …, alors … »."""

    type: Literal["decision"]
    titre: str
    situation: str = Field(description="La question ou la situation de départ")
    cas: list[Cas] = Field(description="2 à 6 cas")
    passages: Refs


class ExempleBloc(BaseModel):
    """Un exemple ou un exercice résolu que le cours donne."""

    type: Literal["exemple"]
    titre: str
    enonce: str
    resolution: list[str] = Field(description="Les étapes de la résolution, 1 à 6")
    resultat: str = Field(description="Ce qu'on retient de l'exemple")
    passages: Refs


class Piege(BaseModel):
    erreur: str = Field(description="L'erreur ou la confusion")
    correction: str = Field(description="Ce qui est juste, selon le cours")


class PiegeBloc(BaseModel):
    """Confusions entre des éléments du cours, ou erreurs que le cours signale lui-même."""

    type: Literal["piege"]
    titre: str
    pieges: list[Piege] = Field(description="1 à 5 pièges")
    passages: Refs


class EssentielBloc(BaseModel):
    """Ce qu'il faut retenir de la section, en quelques lignes."""

    type: Literal["essentiel"]
    titre: str
    points: list[str] = Field(description="3 à 8 lignes, une idée par ligne")
    passages: Refs


class QuestionReponse(BaseModel):
    question: str = Field(description="Question précise qui appelle une réponse courte")
    reponse: str = Field(description="1 à 2 phrases, exactes selon le cours")


class AutotestBloc(BaseModel):
    type: Literal["autotest"]
    titre: str
    questions: list[QuestionReponse] = Field(description="2 à 4 questions")
    passages: Refs


Bloc = Annotated[
    TexteBloc
    | DefinitionBloc
    | EncadreBloc
    | TableauBloc
    | EtapesBloc
    | FriseBloc
    | DecisionBloc
    | ExempleBloc
    | PiegeBloc
    | EssentielBloc
    | AutotestBloc,
    Field(discriminator="type"),
]


def bloc_as_text(bloc: Bloc) -> str:
    """Le contenu d'un bloc à plat, pour le vérificateur et la mesure de couverture."""
    if isinstance(bloc, TexteBloc):
        return bloc.contenu
    if isinstance(bloc, DefinitionBloc):
        return f"{bloc.titre} : {bloc.definition} {bloc.exemple}".strip()
    if isinstance(bloc, EncadreBloc):
        parts = [f"{bloc.nature} : {bloc.enonce}"]
        if bloc.conditions:
            parts.append("Conditions : " + " ; ".join(bloc.conditions))
        if bloc.variables:
            parts.append(
                "Où " + " ; ".join(f"{v.symbole} = {v.signification}" for v in bloc.variables)
            )
        if bloc.idee:
            parts.append(bloc.idee)
        return "\n".join(parts)
    if isinstance(bloc, TableauBloc):
        rows = [" | ".join(bloc.colonnes)] + [" | ".join(row) for row in bloc.lignes]
        return "\n".join(rows)
    if isinstance(bloc, EtapesBloc):
        return "\n".join(f"{i}. {e.titre} : {e.detail}" for i, e in enumerate(bloc.etapes, 1))
    if isinstance(bloc, FriseBloc):
        return "\n".join(f"{e.repere} : {e.evenement}" for e in bloc.evenements)
    if isinstance(bloc, DecisionBloc):
        return bloc.situation + "\n" + "\n".join(f"Si {c.si}, alors {c.alors}" for c in bloc.cas)
    if isinstance(bloc, ExempleBloc):
        return "\n".join([bloc.enonce, *bloc.resolution, bloc.resultat])
    if isinstance(bloc, PiegeBloc):
        return "\n".join(f"Erreur : {p.erreur} Correction : {p.correction}" for p in bloc.pieges)
    if isinstance(bloc, EssentielBloc):
        return "\n".join(f"- {p}" for p in bloc.points)
    return "\n".join(f"Q : {q.question} R : {q.reponse}" for q in bloc.questions)


# --- Sorties demandées au modèle ----------------------------------------------------------------


class PlanSection(BaseModel):
    section: int = Field(description="Numéro de la section, tel que donné")
    titre: str = Field(description="Titre de la section dans la fiche, court et parlant")
    blocs: list[BlockKind] = Field(description="Les types de blocs à produire, dans l'ordre")
    consigne: str = Field(
        description="Ce que chaque bloc doit contenir et mettre en avant, en 1 à 3 phrases ; "
        "quelles notions relier à d'autres sections"
    )


class FichePlan(BaseModel):
    """Sortie de l'appel plan : le parcours de la fiche avant toute rédaction."""

    titre: str = Field(description="Titre de la fiche, celui du cours ou mieux")
    accroche: str = Field(description="2 phrases : de quoi parle le cours et pourquoi ça compte")
    fil_conducteur: str = Field(
        description="3 à 5 phrases : comment les sections s'enchaînent, ce qui relie les notions"
    )
    sections: list[PlanSection]


class SectionBlocs(BaseModel):
    """Sortie de l'appel blocs : les blocs d'une section, dans l'ordre de lecture."""

    blocs: list[Bloc]


class Verdict(BaseModel):
    bloc: int = Field(description="Numéro du bloc, tel que donné")
    soutenu: bool = Field(description="Vrai si tout ce que le bloc affirme est dans les extraits")
    probleme: str = Field(description="Ce qui n'est pas soutenu, ou vide")


class Verdicts(BaseModel):
    """Sortie de l'appel vérification : un verdict par bloc."""

    verdicts: list[Verdict]


class Suggestion(BaseModel):
    """Sortie de l'appel suggestion : le gabarit qui convient au cours."""

    gabarit: str = Field(description="Identifiant d'un des gabarits proposés")
    raison: str = Field(description="Une phrase")


# --- La fiche assemblée (contrat de sortie v1) --------------------------------------------------

Statut = Literal["ok", "echec", "budget"]


class BlocFiche(BaseModel):
    bloc: Bloc
    passage_ids: list[str] = Field(default_factory=list)
    pages: list[int] = Field(default_factory=list)
    verifie: bool | None = Field(
        default=None, description="Vrai : soutenu par ses passages ; None : non vérifié"
    )


class SectionFiche(BaseModel):
    section_id: str
    titre: str
    statut: Statut = "ok"
    message: str = ""
    blocs: list[BlocFiche] = Field(default_factory=list)
    rejetes: list[BlocFiche] = Field(
        default_factory=list, description="Blocs retirés par la vérification, gardés pour le banc"
    )


class ChapitreFiche(BaseModel):
    section_id: str | None = None
    titre: str = ""
    sections: list[SectionFiche]


class Couverture(BaseModel):
    """Les notions essentielles du cours (importance 3) et celles que la fiche nomme."""

    essentielles: int = 0
    couvertes: int = 0
    manquantes: list[str] = Field(default_factory=list)


class GabaritInfo(BaseModel):
    id: str
    version: int
    nom: str
    suggere: bool = False
    raison: str = ""


class Usage(BaseModel):
    calls: int = 0
    cached_calls: int = 0
    failed_calls: int = 0
    retries: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    judge_calls: int = 0
    judge_input_tokens: int = 0
    judge_output_tokens: int = 0
    judge_cost_usd: float = 0.0


class Fiche(BaseModel):
    """Contrat de sortie du module, version 1."""

    schema_version: Literal["1"] = "1"
    document_id: str
    document_title: str
    gabarit: GabaritInfo
    titre: str
    accroche: str
    fil_conducteur: str
    chapitres: list[ChapitreFiche]
    couverture: Couverture = Field(default_factory=Couverture)
    usage: Usage = Field(default_factory=Usage)
    metrics: dict[str, float | int | str] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)

    def sections(self) -> list[SectionFiche]:
        return [s for c in self.chapitres for s in c.sections]

    def blocs(self) -> list[BlocFiche]:
        return [b for s in self.sections() for b in s.blocs]
