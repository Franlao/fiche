"""CLI : generer, suggerer, gabarits, rendre, schema, config-example."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import typer
from rich.console import Console

from fiche.config import env_example, get_settings

app = typer.Typer(help="Module fiche de révision.", no_args_is_help=True)
console = Console()


@app.callback()
def _setup(verbose: bool = typer.Option(False, "--verbose", "-v")) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )


@app.command()
def generer(
    course: Path = typer.Argument(..., exists=True, help="Résultat v1 d'ingest (JSON)"),
    gabarit: str | None = typer.Option(None, help="Identifiant du gabarit ; vide : suggéré"),
    llm: str | None = typer.Option(None, help="fournisseur:modèle du rédacteur"),
    out: Path = typer.Option(Path("out"), help="Dossier de sortie"),
    sans_verification: bool = typer.Option(False, "--sans-verification"),
    budget: float | None = typer.Option(None, help="Plafond en dollars pour cette fiche"),
) -> None:
    """Produit la fiche d'un cours : JSON (contrat) et HTML (pour juger sur pièces)."""
    from fiche.course import Course
    from fiche.render import render_html
    from fiche.request import FicheRequest
    from fiche.run import run

    request = FicheRequest(
        course=course,
        gabarit=gabarit,
        llm=llm,
        verify=False if sans_verification else None,
        max_cost_usd=budget,
    )
    fiche = run(
        request,
        get_settings(),
        on_event=lambda step, msg: console.print(f"[bold]{step}[/bold] {msg}"),
    )
    out.mkdir(parents=True, exist_ok=True)
    stem = course.stem
    (out / f"{stem}.fiche.json").write_text(fiche.model_dump_json(indent=2), encoding="utf-8")
    (out / f"{stem}.fiche.html").write_text(
        render_html(fiche, Course.load(course)), encoding="utf-8"
    )
    for err in fiche.errors:
        console.print(f"[yellow]{err}[/yellow]")
    console.print(json.dumps(fiche.metrics, ensure_ascii=False, indent=2))
    console.print(f"Fiche : {out / f'{stem}.fiche.html'}")


@app.command()
def suggerer(course: Path = typer.Argument(..., exists=True)) -> None:
    """Le gabarit que le module proposerait pour ce cours (un appel court)."""
    from fiche.cache import DiskCache
    from fiche.course import Course
    from fiche.gabarits import load_gabarits
    from fiche.llm import build_writer
    from fiche.run import suggest_gabarit, writing_units

    settings = get_settings()
    loaded = Course.load(course)
    writer = build_writer(settings, DiskCache(settings.cache_dir, settings.cache_enabled))
    gabarit, raison, cost = suggest_gabarit(
        writer, loaded, writing_units(loaded), load_gabarits(settings.gabarits_dir)
    )
    console.print(f"{gabarit.id} : {raison} ({cost:.4f} $)")


@app.command()
def gabarits() -> None:
    """Les gabarits disponibles, avec ce que l'étudiant en lit."""
    from fiche.gabarits import load_gabarits

    for g in load_gabarits(get_settings().gabarits_dir).values():
        console.print(f"[bold]{g.id}[/bold] v{g.version} : {g.nom} ({', '.join(g.filieres)})")
        console.print("  " + " ".join(g.pour_etudiant.split()))
        console.print("  blocs : " + ", ".join(g.allowed()))


@app.command()
def rendre(
    fiche_json: Path = typer.Argument(..., exists=True),
    course: Path | None = typer.Option(None, help="Le cours, pour montrer les extraits"),
    out: Path | None = typer.Option(None),
) -> None:
    """Rend en HTML une fiche déjà produite."""
    from fiche.course import Course
    from fiche.models import Fiche
    from fiche.render import render_html

    fiche = Fiche.model_validate_json(fiche_json.read_text(encoding="utf-8"))
    target = out or fiche_json.with_suffix(".html")
    target.write_text(render_html(fiche, Course.load(course) if course else None), encoding="utf-8")
    console.print(f"HTML : {target}")


@app.command()
def schema(out: Path = typer.Option(Path("docs/schema/fiche-v1.json"))) -> None:
    """Écrit le schéma JSON du contrat de sortie (Fiche v1)."""
    from fiche.models import Fiche

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(Fiche.model_json_schema(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    console.print(f"Schéma : {out}")


@app.command("config-example")
def config_example(out: Path = typer.Option(Path(".env.example"))) -> None:
    """Écrit .env.example depuis les réglages documentés."""
    out.write_text(env_example(), encoding="utf-8")
    console.print(f"Configuration : {out}")
