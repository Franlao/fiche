from pathlib import Path

from fiche.course import Course
from fiche.ecriture import mesurer, nettoyer, tics
from fiche.run import writing_units


def test_tics_are_counted():
    texte = (
        "Il est important de noter que la pompe joue un rôle clé — ex : la notion clé. "
        "Elle permet de transporter, elle permet de stocker... Véritable cœur du sujet !"
    )
    found = tics(texte)
    for name in (
        "il est important",
        "rôle clé",
        "tiret",
        "ex deux-points",
        "clé adjectif",
        "permet de",
        "points de suspension",
        "véritable",
        "exclamation",
    ):
        assert name in found, name
    assert found["permet de"] == 2
    assert tics("La pompe expulse trois ions sodium.") == {}
    mesure = mesurer("Un deux trois — quatre")
    assert (mesure.mots, mesure.total, mesure.pour_mille_mots) == (5, 1, 200.0)


def test_cleaning_keeps_the_meaning():
    assert nettoyer("entre 5–15 mM") == "entre 5 à 15 mM"
    assert nettoyer("La pompe — une ATPase — expulse le sodium.") == (
        "La pompe, une ATPase, expulse le sodium."
    )
    assert nettoyer("Deux types — actif et passif.") == "Deux types, actif et passif."
    assert nettoyer("Les ions Na, K, Cl...") == "Les ions Na, K, Cl"
    assert nettoyer("Le tiret-du-6 reste") == "Le tiret-du-6 reste"
    assert nettoyer("Le **sarcomère** raccourcit") == "Le sarcomère raccourcit"
    assert "des X aux Y" in tics(
        "Elle décrit tout, des trajectoires planétaires aux mécanismes industriels."
    )
    assert nettoyer("$x - y$ et $a-b$") == "$x - y$ et $a-b$"


def test_chapter_ends_are_marked(course_path: Path):
    course = Course.load(course_path)
    units = writing_units(course, min_chars=1)
    assert [u.fin_chapitre for u in units] == [False, True, False, True]
