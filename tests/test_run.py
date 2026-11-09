"""La chaîne complète avec le faux modèle : plan, blocs, vérification, assemblage, budget,
rendu."""

from pathlib import Path
from typing import Any

import pytest

from fiche.cache import DiskCache
from fiche.config import Settings
from fiche.course import Course
from fiche.errors import ProviderError, UnknownGabarit
from fiche.llm import FakeLLMProvider
from fiche.models import Fiche, SectionBlocs, Suggestion, Verdict, Verdicts
from fiche.render import render_html
from fiche.request import FicheRequest
from fiche.run import coverage, run
from tests.conftest import default_blocs, default_handler, default_plan, default_verdicts


def test_full_run_assembles_a_fiche_anchored_to_passages(
    course_path: Path, settings: Settings, fake: FakeLLMProvider
):
    events: list[tuple[str, str]] = []
    fiche = run(
        FicheRequest(course=course_path, gabarit="sciences-formelles"),
        settings,
        writer=fake,
        judge=fake,
        on_event=lambda step, msg: events.append((step, msg)),
    )
    assert fiche.titre == "Mécanique des fluides, l'essentiel"
    assert [c.titre for c in fiche.chapitres] == ["Statique des fluides", "Fluides réels"]
    sections = fiche.sections()
    assert all(s.statut == "ok" for s in sections)
    first = sections[0].blocs
    assert [b.bloc.type for b in first] == ["definition", "encadre", "tableau", "essentiel"]
    # numéros d'extraits convertis en identifiants et pages
    assert first[0].passage_ids == ["p1"] and first[0].pages == [1]
    assert all(b.verifie is True for b in first)
    assert fiche.gabarit.id == "sciences-formelles" and not fiche.gabarit.suggere
    # couverture : trois notions essentielles, toutes nommées par les blocs
    assert (fiche.couverture.essentielles, fiche.couverture.couvertes) == (3, 3)
    assert fiche.metrics["part_structuree"] == 1.0 and fiche.metrics["blocs_rejetes"] == 0
    assert fiche.usage.calls == 1 + 2 * len(sections)  # plan, blocs et verdicts par unité
    assert fiche.usage.cost_usd == 0.0
    assert [e[0] for e in events][:2] == ["unites", "plan"]
    # schéma stable : la fiche se relit
    assert Fiche.model_validate_json(fiche.model_dump_json()).blocs()


def test_gabarit_is_suggested_when_not_given(
    course_path: Path, settings: Settings, fake: FakeLLMProvider
):
    fiche = run(FicheRequest(course=course_path), settings, writer=fake, judge=None)
    assert fiche.gabarit.suggere and fiche.gabarit.id == "sciences-formelles"
    assert fiche.gabarit.raison == "des formules"
    assert all(b.verifie is None for b in fiche.blocs())  # pas de vérificateur
    with pytest.raises(UnknownGabarit):
        run(FicheRequest(course=course_path, gabarit="droit"), settings, writer=fake, judge=None)


def test_unsupported_blocks_are_removed_and_kept_for_the_bench(
    course_path: Path, settings: Settings
):
    def handler(system: str, user: str, schema: type[Any]) -> Any:
        if schema is Verdicts:
            n = len(default_verdicts(user).verdicts)
            verdicts = [
                Verdict(bloc=i, soutenu=i != 2, probleme="" if i != 2 else "formule inventée")
                for i in range(1, n + 1)
            ]
            return Verdicts(verdicts=verdicts)
        return default_handler(system, user, schema)

    fake = FakeLLMProvider(DiskCache(settings.cache_dir), handler)
    fiche = run(
        FicheRequest(course=course_path, gabarit="sciences-formelles"),
        settings,
        writer=fake,
        judge=fake,
    )
    for section in fiche.sections():
        assert [b.bloc.type for b in section.blocs] == ["definition", "tableau", "essentiel"]
        assert [b.bloc.type for b in section.rejetes] == ["encadre"]
        assert section.rejetes[0].verifie is False
    assert fiche.metrics["blocs_rejetes"] == len(fiche.sections())
    assert any("formule inventée" in err for err in fiche.errors)


def test_budget_stops_the_remaining_units_without_failing(course_path: Path, settings: Settings):
    fake = FakeLLMProvider(DiskCache(settings.cache_dir), default_handler, cost=0.30)
    settings = settings.model_copy(update={"max_cost_usd": 0.50, "llm_concurrency": 1})
    fiche = run(
        FicheRequest(course=course_path, gabarit="sciences-formelles"),
        settings,
        writer=fake,
        judge=None,
    )
    statuts = [s.statut for s in fiche.sections()]
    assert statuts[0] == "ok" and "budget" in statuts
    assert fiche.metrics["spent_usd"] >= 0.50
    assert any("budget" in err for err in fiche.errors)


def test_a_failing_unit_does_not_block_the_fiche(course_path: Path, settings: Settings):
    calls = {"blocs": 0}

    def handler(system: str, user: str, schema: type[Any]) -> Any:
        if schema is SectionBlocs:
            calls["blocs"] += 1
            if "transmet intégralement" in user:
                return SectionBlocs(blocs=[])  # refusé par le check à chaque fois
        return default_handler(system, user, schema)

    fake = FakeLLMProvider(DiskCache(settings.cache_dir), handler)
    settings = settings.model_copy(update={"llm_concurrency": 1})
    fiche = run(
        FicheRequest(course=course_path, gabarit="sciences-formelles"),
        settings,
        writer=fake,
        judge=None,
    )
    failed = [s for s in fiche.sections() if s.statut == "echec"]
    assert len(failed) == 1 and "fake" in failed[0].message and not failed[0].blocs
    assert fiche.usage.retries >= 2  # le faux a été redemandé


def test_plan_failure_is_raised(course_path: Path, settings: Settings):
    def handler(system: str, user: str, schema: type[Any]) -> Any:
        if schema.__name__ == "FichePlan":
            plan = default_plan(user)
            plan.sections = plan.sections[:1]  # toujours incomplet
            return plan
        return default_handler(system, user, schema)

    fake = FakeLLMProvider(DiskCache(settings.cache_dir), handler)
    with pytest.raises(ProviderError):
        run(
            FicheRequest(course=course_path, gabarit="sciences-formelles"),
            settings,
            writer=fake,
            judge=None,
        )


def test_coverage_matches_names_loosely(course_path: Path):
    course = Course.load(course_path)
    result = coverage(course, "Le théorème de PASCAL ; la pression ; les fluides parfaits")
    assert (result.essentielles, result.couvertes) == (3, 3)
    partial = coverage(course, "rien à voir")
    assert partial.couvertes == 0 and set(partial.manquantes) == {
        "Fluide parfait",
        "Pression",
        "Théorème de Pascal",
    }


def test_html_render_shows_every_block_form(
    course_path: Path, settings: Settings, fake: FakeLLMProvider
):
    fiche = run(
        FicheRequest(course=course_path, gabarit="sciences-formelles"),
        settings,
        writer=fake,
        judge=fake,
    )
    html = render_html(fiche, Course.load(course_path))
    assert "<table>" in html and 'class="bloc encadre"' in html and "formule" in html
    assert "Voir le passage du cours" in html and '<span class="page">p. 1</span>' in html
    assert "Mesures du labo" in html and "mathjax" in html
    assert "À retenir du chapitre" in html
    # forme humaine : pas d'étiquette en capitales, pas de symboles à la place de la mise en page
    assert "text-transform: uppercase" not in html and "✗" not in html and "✓" not in html
    assert "Voir le passage du cours" not in render_html(fiche)  # sans le cours, pas d'extraits


def test_request_options_override_settings(settings: Settings):
    request = FicheRequest(
        course=Path("x.json"), llm="openai:gpt-6.1-sol", verify=False, max_cost_usd=0.2
    )
    merged = request.settings(settings)
    assert (merged.llm_provider, merged.llm_model, merged.verify, merged.max_cost_usd) == (
        "openai",
        "gpt-6.1-sol",
        False,
        0.2,
    )


def test_default_blocs_fixture_is_valid_for_three_extracts():
    assert len(default_blocs("[1] a\n[2] b\n[3] c").blocs) == 4
    assert Suggestion(gabarit="x", raison="y").gabarit == "x"


def test_lost_characters_are_written_as_entities():
    from fiche.render import e

    assert e("� 95 % <b>") == "&#xFFFD; 95 % &lt;b&gt;"


def test_writing_is_cleaned_and_measured_at_assembly(course_path: Path, settings: Settings):
    def handler(system: str, user: str, schema: type[Any]) -> Any:
        if schema is SectionBlocs:
            out = default_blocs(user)
            first = out.blocs[0]
            assert first.type == "definition"
            first.definition = "Un fluide — sans viscosité — coule bien… entre 5–15 °C"
            return out
        return default_handler(system, user, schema)

    fake = FakeLLMProvider(DiskCache(settings.cache_dir), handler)
    fiche = run(
        FicheRequest(course=course_path, gabarit="sciences-formelles"),
        settings,
        writer=fake,
        judge=None,
    )
    bloc = fiche.blocs()[0].bloc
    assert bloc.type == "definition"
    assert bloc.definition == "Un fluide, sans viscosité, coule bien entre 5 à 15 °C"
    assert fiche.metrics["tics"] == 0 and fiche.metrics["mots"] > 0
    assert "titres_en_formule" in fiche.metrics and "monotonie" in fiche.metrics
