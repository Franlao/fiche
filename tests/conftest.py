"""Un petit cours au contrat v1, écrit à la main (aucun texte tiré du corpus), et un faux
modèle qui répond selon le schéma demandé."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from fiche.cache import DiskCache
from fiche.config import Settings
from fiche.llm import FakeLLMProvider
from fiche.models import (
    FichePlan,
    PlanSection,
    SectionBlocs,
    Suggestion,
    Verdict,
    Verdicts,
)


def _passage(i: int, text: str, page: int) -> dict[str, Any]:
    return {
        "id": f"p{i}",
        "doc_id": "doc",
        "order": i,
        "text": text,
        "page_start": page,
        "page_end": page,
        "char_start": 0,
        "char_end": len(text),
        "anchors": [{"page": page, "bbox": [0.1, 0.1, 0.9, 0.3]}],
    }


COURSE: dict[str, Any] = {
    "schema_version": "1",
    "document": {
        "id": "doc",
        "title": "Cours fictif de mécanique des fluides",
        "source_file": "fictif.pdf",
        "source_type": "pdf_native",
        "page_count": 4,
        "conversion_tool": "test",
    },
    "passages": [
        _passage(1, "Un fluide parfait est un fluide sans viscosité. " * 30, 1),
        _passage(2, "La pression est une force par unité de surface : $p = F/S$. " * 30, 1),
        _passage(
            3, "Le théorème de Pascal dit que la pression se transmet intégralement. " * 30, 2
        ),
        _passage(4, "Un fluide réel a une viscosité non nulle, notée $\\mu$. " * 30, 3),
        _passage(5, "Le nombre de Reynolds compare inertie et viscosité. " * 30, 3),
        _passage(6, "Conclusion : résumé du chapitre. " * 10, 4),
    ],
    "sections": [
        {"id": "c1", "order": 0, "title": "Statique des fluides", "depth": 1},
        {
            "id": "s1",
            "order": 1,
            "title": "Fluide parfait et pression",
            "passage_ids": ["p1", "p2"],
            "notion_ids": ["n1", "n2"],
            "parent_id": "c1",
            "depth": 2,
        },
        {
            "id": "s2",
            "order": 2,
            "title": "Théorème de Pascal",
            "passage_ids": ["p3"],
            "notion_ids": ["n3"],
            "parent_id": "c1",
            "depth": 2,
        },
        {"id": "c2", "order": 3, "title": "Fluides réels", "depth": 1},
        {
            "id": "s3",
            "order": 4,
            "title": "Viscosité et Reynolds",
            "passage_ids": ["p4", "p5"],
            "notion_ids": ["n4"],
            "parent_id": "c2",
            "depth": 2,
        },
        {
            "id": "s4",
            "order": 5,
            "title": "Conclusion",
            "passage_ids": ["p6"],
            "parent_id": "c2",
            "depth": 2,
        },
    ],
    "notions": [
        {
            "id": "n1",
            "name": "Fluide parfait",
            "definition": "Fluide sans viscosité.",
            "type": "definition",
            "importance": 3,
            "passage_ids": ["p1"],
            "section_id": "s1",
            "points": ["sans viscosité"],
        },
        {
            "id": "n2",
            "name": "Pression",
            "definition": "Force par unité de surface.",
            "type": "formula",
            "importance": 3,
            "passage_ids": ["p2"],
            "section_id": "s1",
        },
        {
            "id": "n3",
            "name": "Théorème de Pascal",
            "definition": "La pression se transmet intégralement.",
            "type": "theorem",
            "importance": 3,
            "passage_ids": ["p3"],
            "section_id": "s2",
        },
        {
            "id": "n4",
            "name": "Nombre de Reynolds",
            "definition": "Rapport inertie sur viscosité.",
            "type": "definition",
            "importance": 2,
            "passage_ids": ["p5"],
            "section_id": "s3",
        },
    ],
}


@pytest.fixture
def course_path(tmp_path: Path) -> Path:
    path = tmp_path / "cours.json"
    path.write_text(json.dumps(COURSE, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        llm_provider="fake",
        judge_provider="fake",
        verify=False,  # un vérificateur passé à run() sert quand même
        cache_dir=tmp_path / "cache",
        cache_enabled=True,
        _env_file=None,
    )


def default_blocs(user: str) -> SectionBlocs:
    """Des blocs plausibles pour n'importe quelle unité : un encadré, un tableau, l'essentiel."""
    n = len(re.findall(r"^\[(\d+)\]", user, flags=re.M))
    return SectionBlocs.model_validate(
        {
            "blocs": [
                {
                    "type": "definition",
                    "titre": "Fluide parfait",
                    "definition": "Un fluide sans viscosité.",
                    "exemple": "",
                    "passages": [1],
                },
                {
                    "type": "encadre",
                    "nature": "formule",
                    "titre": "Pression",
                    "enonce": "$p = F/S$",
                    "conditions": [],
                    "variables": [{"symbole": "F", "signification": "force"}],
                    "idee": "",
                    "passages": [min(2, n)],
                },
                {
                    "type": "tableau",
                    "titre": "Fluides",
                    "colonnes": ["Type", "Viscosité"],
                    "lignes": [["parfait", "nulle"], ["réel", "non nulle"]],
                    "passages": [1, n],
                },
                {
                    "type": "essentiel",
                    "titre": "L'essentiel",
                    "points": ["La pression est une force par surface", "Théorème de Pascal"],
                    "passages": [1],
                },
            ]
        }
    )


def default_plan(user: str) -> FichePlan:
    numbers = [int(m) for m in re.findall(r"^\[(\d+)\]", user, flags=re.M)]
    return FichePlan(
        titre="Mécanique des fluides, l'essentiel",
        accroche="Deux phrases d'accroche.",
        fil_conducteur="Du fluide parfait au fluide réel.",
        sections=[
            PlanSection(
                section=i,
                titre=f"Unité {i}",
                blocs=["definition", "encadre", "tableau", "essentiel"],
                consigne="Encadrer la formule de la pression.",
            )
            for i in numbers
        ],
    )


def default_verdicts(user: str) -> Verdicts:
    n = len(re.findall(r"^\((\d+)\)", user, flags=re.M))
    return Verdicts(verdicts=[Verdict(bloc=i, soutenu=True, probleme="") for i in range(1, n + 1)])


def default_handler(system: str, user: str, schema: type[Any]) -> Any:
    if schema is FichePlan:
        return default_plan(user)
    if schema is SectionBlocs:
        return default_blocs(user)
    if schema is Verdicts:
        return default_verdicts(user)
    if schema is Suggestion:
        return Suggestion(gabarit="sciences-formelles", raison="des formules")
    raise AssertionError(f"schéma inattendu : {schema}")


@pytest.fixture
def fake(settings: Settings) -> FakeLLMProvider:
    return FakeLLMProvider(DiskCache(settings.cache_dir), default_handler)
