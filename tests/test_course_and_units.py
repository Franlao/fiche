from pathlib import Path

import pytest

from fiche.course import Course
from fiche.errors import InvalidCourse
from fiche.run import writing_units


def test_course_loads_the_contract_and_groups_by_chapter(course_path: Path):
    course = Course.load(course_path)
    assert [s.id for s in course.leaf_sections()] == ["s1", "s2", "s3", "s4"]
    chapters = course.chapters()
    assert [(c.title if c else None, [s.id for s in ss]) for c, ss in chapters] == [
        ("Statique des fluides", ["s1", "s2"]),
        ("Fluides réels", ["s3", "s4"]),
    ]
    assert [n.name for n in course.notions_of(course.sections[1])] == ["Fluide parfait", "Pression"]


def test_small_sections_are_written_together(course_path: Path):
    course = Course.load(course_path)
    units = writing_units(course, min_chars=100_000)  # tout regrouper par chapitre
    assert [[s.id for s in u.sections] for u in units] == [["s1", "s2"], ["s3", "s4"]]
    assert units[0].title == "Fluide parfait et pression · Théorème de Pascal"
    assert [n.name for n in units[0].notions] == [
        "Fluide parfait",
        "Pression",
        "Théorème de Pascal",
    ]
    one_each = writing_units(course, min_chars=1)
    assert [[s.id for s in u.sections] for u in one_each] == [["s1"], ["s2"], ["s3"], ["s4"]]
    assert [u.index for u in one_each] == [1, 2, 3, 4]


def test_a_long_section_is_split_into_several_units(course_path: Path):
    course = Course.load(course_path)
    units = writing_units(course, min_chars=1, max_chars=1600)
    first = [u for u in units if u.sections[0].id == "s1"]
    assert len(first) == 2 and all(len(u.passages) == 1 for u in first)


def test_invalid_course_is_refused(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    with pytest.raises(InvalidCourse):
        Course.load(bad)
    empty = tmp_path / "empty.json"
    empty.write_text(
        '{"document": {"id": "d", "title": "t"}, "passages": [], "sections": []}',
        encoding="utf-8",
    )
    with pytest.raises(InvalidCourse, match="aucune section"):
        Course.load(empty)
