from pathlib import Path

import pytest
import yaml

from fiche.config import env_example
from fiche.errors import UnknownGabarit
from fiche.gabarits import BUILTIN_DIR, Gabarit, get_gabarit, load_gabarits
from fiche.models import BLOCK_KINDS, FichePlan, PlanSection, SectionBlocs, Verdict, Verdicts
from fiche.run import Unit, check_blocs, check_plan, check_verdicts

ROOT = Path(__file__).resolve().parents[1]


def test_builtin_gabarits_are_valid_and_cover_the_two_first_families():
    gabarits = load_gabarits()
    assert {"sciences-formelles", "vivant-sante"} <= set(gabarits)
    for g in gabarits.values():
        assert set(g.allowed()) <= set(BLOCK_KINDS)
        assert "essentiel" in g.allowed() and "autotest" in g.allowed()
        assert g.max_texte_par_section <= 1
        assert g.plan and g.redaction and g.pour_etudiant
    with pytest.raises(UnknownGabarit, match="connus"):
        get_gabarit("inconnu")


def test_gabarit_rejects_unknown_block_types_and_duplicates():
    data = yaml.safe_load((BUILTIN_DIR / "sciences-formelles.yaml").read_text("utf-8"))
    data["blocs"].append({"type": "video", "usage": "non"})
    with pytest.raises(ValueError, match="inconnu"):
        Gabarit.model_validate(data)
    data["blocs"].pop()
    data["blocs"].append(dict(data["blocs"][0]))
    with pytest.raises(ValueError, match="répété"):
        Gabarit.model_validate(data)


def _units(*ends: bool) -> list[Unit]:
    return [
        Unit(index=i, title=f"u{i}", chapter=None, sections=[], passages=[], fin_chapitre=end)
        for i, end in enumerate(ends, start=1)
    ]


def test_plan_check_wants_every_unit_once_with_permitted_blocks():
    g = get_gabarit("sciences-formelles")
    check = check_plan(_units(False, True), g)
    ok = FichePlan(
        titre="t",
        accroche="a",
        fil_conducteur="f",
        sections=[
            PlanSection(section=1, titre="u1", blocs=["definition"], consigne="c"),
            PlanSection(
                section=2, titre="u2", blocs=["encadre", "essentiel", "autotest"], consigne="c"
            ),
        ],
    )
    assert check(ok) is None
    missing = ok.model_copy(update={"sections": ok.sections[:1]})
    assert "de 1 à 2" in (check(missing) or "")
    bad_type = ok.model_copy(deep=True)
    bad_type.sections[0].blocs = ["frise"]  # pas dans le gabarit sciences formelles
    assert "non permis" in (check(bad_type) or "")
    too_much_text = ok.model_copy(deep=True)
    too_much_text.sections[0].blocs = ["texte", "texte"]
    assert "bloc texte" in (check(too_much_text) or "")


def test_plan_check_keeps_summary_and_quiz_for_chapter_ends():
    g = get_gabarit("vivant-sante")
    check = check_plan(_units(False, True), g)
    early = FichePlan(
        titre="t",
        accroche="a",
        fil_conducteur="f",
        sections=[
            PlanSection(section=1, titre="u1", blocs=["etapes", "essentiel"], consigne="c"),
            PlanSection(section=2, titre="u2", blocs=["tableau"], consigne="c"),
        ],
    )
    message = check(early) or ""
    assert "section 1 : essentiel seulement en fin de chapitre" in message
    assert "section 2 (fin de chapitre) : il manque essentiel, autotest" in message


def test_gabarit_closing_blocks_must_be_allowed():
    data = yaml.safe_load((BUILTIN_DIR / "vivant-sante.yaml").read_text("utf-8"))
    data["fin_de_chapitre"] = ["exemple"]
    with pytest.raises(ValueError, match="fin_de_chapitre"):
        Gabarit.model_validate(data)


def test_blocs_check_reports_every_problem_at_once():
    g = get_gabarit("vivant-sante")
    check = check_blocs(3, g)
    out = SectionBlocs.model_validate(
        {
            "blocs": [
                {
                    "type": "tableau",
                    "titre": "t",
                    "colonnes": ["a", "b"],
                    "lignes": [["x"]],
                    "passages": [4],
                },
                {
                    "type": "etapes",
                    "titre": "e",
                    "etapes": [{"titre": "a", "detail": "b"}],
                    "passages": [],
                },
                {
                    "type": "exemple",
                    "titre": "x",
                    "enonce": "e",
                    "resolution": ["r"],
                    "resultat": "s",
                    "passages": [1],
                },
            ]
        }
    )
    message = check(out) or ""
    assert "bloc 1 : extraits inexistants [4]" in message
    assert "2 cellules" in message
    assert "bloc 2 : aucun extrait" in message and "deux étapes" in message
    assert "bloc 3 : type exemple non permis" in message
    assert check(SectionBlocs(blocs=[])) is not None


def test_verdicts_check_wants_one_verdict_per_block():
    check = check_verdicts(2)
    assert check(Verdicts(verdicts=[Verdict(bloc=1, soutenu=True, probleme="")])) is not None
    assert (
        check(
            Verdicts(
                verdicts=[
                    Verdict(bloc=1, soutenu=True, probleme=""),
                    Verdict(bloc=2, soutenu=False, probleme="chiffre"),
                ]
            )
        )
        is None
    )


def test_env_example_and_schema_are_up_to_date():
    assert (ROOT / ".env.example").read_text(encoding="utf-8") == env_example()
    assert "FICHE_MAX_COST_USD=0.5" in env_example()
    import json

    from fiche.models import Fiche

    published = json.loads((ROOT / "docs/schema/fiche-v1.json").read_text(encoding="utf-8"))
    assert published == Fiche.model_json_schema()
