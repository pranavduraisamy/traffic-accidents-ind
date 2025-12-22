# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jinja2==3.1.3",
#     "fire==0.7.0",
#     "loguru==0.7.0"
# ]
# ///

import subprocess
from typing import List, Union
from pathlib import Path

import jinja2
import fire

from loguru import logger


def _export_html_wasm(notebook_path: Path, output_dir: Path) -> bool:
    output_path: Path = notebook_path.with_suffix(".html")
    cmd: List[str] = ["uvx", "marimo", "export", "html-wasm", "--sandbox"]
    logger.info(f"Exporting {notebook_path} to {output_path} as a page")
    cmd.extend(["--mode", "run", "--no-show-code"])
    try:
        output_file: Path = output_dir / notebook_path.with_suffix(".html")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        cmd.extend([str(notebook_path), "-o", str(output_file)])
        logger.debug(f"Running command: {cmd}")
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Successfully exported {notebook_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error exporting {notebook_path}:")
        logger.error(f"Command output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error exporting {notebook_path}: {e}")
        return False


def _generate_index(
    output_dir: Path,
    template_file: Path,
    notebooks_data: List[dict] | None = None,
    apps_data: List[dict] | None = None,
) -> None:
    logger.info("Generating index.html")
    index_path: Path = output_dir / "index.html"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        template_dir = template_file.parent
        template_name = template_file.name
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )
        template = env.get_template(template_name)
        rendered_html = template.render(notebooks=notebooks_data, apps=apps_data)
        with open(index_path, "w") as f:
            f.write(rendered_html)
        logger.info(f"Successfully generated index.html at {index_path}")
    except IOError as e:
        logger.error(f"Error generating index.html: {e}")
    except jinja2.exceptions.TemplateError as e:
        logger.error(f"Error rendering template: {e}")


def _export(folder: Path, output_dir: Path) -> List[dict]:
    notebooks = list(folder.rglob("*.py"))
    logger.debug(f"Found {len(notebooks)} Python files in {folder}")
    notebook_data = [
        {
            "display_name": (nb.stem.replace("_", " ").title()),
            "html_path": str(nb.with_suffix(".html")),
        }
        for nb in notebooks
        if _export_html_wasm(nb, output_dir)
    ]
    logger.info(
        f"Successfully exported {len(notebook_data)} out of {len(notebooks)} files from {folder}"
    )
    return notebook_data


def main(output_dir: Union[str, Path] = "_site") -> None:
    logger.info("Starting marimo build process")
    output_dir: Path = Path(output_dir)
    logger.info(f"Output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    template_file: Path = Path("assets/index.html.j2")
    logger.info(f"Using template file: {template_file}")
    notebooks_data = _export(Path("notebooks"), output_dir)
    _generate_index(
        output_dir=output_dir,
        notebooks_data=notebooks_data,
        template_file=template_file,
    )
    logger.info(f"Build completed successfully. Output directory: {output_dir}")


if __name__ == "__main__":
    fire.Fire(main)
