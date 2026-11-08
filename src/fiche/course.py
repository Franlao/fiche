"""Le cours d'entrée : le contrat v1 d'ingest, réduit à ce que la fiche utilise.

Les champs inconnus du JSON sont ignorés : le module ne dépend pas du paquet ingest, seulement
de son schéma publié (docs/schema/ingest-result-v1.json dans ingest).
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from fiche.errors import InvalidCourse


class Anchor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    page: int
    bbox: tuple[float, float, float, float] | None = None


class Passage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    order: int
    text: str
    page_start: int
    page_end: int
    anchors: list[Anchor] = Field(default_factory=list)


class Section(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    order: int
    title: str = ""
    passage_ids: list[str] = Field(default_factory=list)
    notion_ids: list[str] = Field(default_factory=list)
    parent_id: str | None = None
    depth: int = 0


class Notion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    definition: str
    type: str = "fact"
    importance: int = 2
    passage_ids: list[str] = Field(default_factory=list)
    section_id: str | None = None
    points: list[str] = Field(default_factory=list)


class DocumentInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    page_count: int = 0
    language: str | None = None


class Course(BaseModel):
    """Un résultat d'ingestion (contrat v1), avec les accès dont la fiche a besoin."""

    model_config = ConfigDict(extra="ignore")
    document: DocumentInfo
    passages: list[Passage]
    sections: list[Section]
    notions: list[Notion] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> Course:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise InvalidCourse(f"{path.name} : {exc}") from exc
        if data.get("schema_version") not in (None, "1"):
            raise InvalidCourse(f"{path.name} : schema_version {data['schema_version']} inconnue")
        course = cls.model_validate(data)
        if not course.leaf_sections():
            raise InvalidCourse(f"{path.name} : aucune section avec des passages")
        return course

    def passage_by_id(self) -> dict[str, Passage]:
        return {p.id: p for p in self.passages}

    def leaf_sections(self) -> list[Section]:
        """Les sections qui portent des passages, dans l'ordre du cours : l'unité de rédaction."""
        return sorted((s for s in self.sections if s.passage_ids), key=lambda s: s.order)

    def chapters(self) -> list[tuple[Section | None, list[Section]]]:
        """Les sections feuilles groupées par chapitre (None quand le cours n'a qu'un niveau)."""
        by_id = {s.id: s for s in self.sections}
        groups: dict[str | None, list[Section]] = {}
        order: list[str | None] = []
        for section in self.leaf_sections():
            parent = section.parent_id if section.parent_id in by_id else None
            if parent not in groups:
                groups[parent] = []
                order.append(parent)
            groups[parent].append(section)
        return [(by_id[key] if key else None, groups[key]) for key in order]

    def passages_of(self, section: Section) -> list[Passage]:
        by_id = self.passage_by_id()
        found = [by_id[pid] for pid in section.passage_ids if pid in by_id]
        return sorted(found, key=lambda p: p.order)

    def notions_of(self, section: Section) -> list[Notion]:
        ids = set(section.notion_ids) | set(section.passage_ids)
        return [
            n
            for n in self.notions
            if n.id in section.notion_ids
            or n.section_id == section.id
            or (not n.section_id and any(p in ids for p in n.passage_ids))
        ]
