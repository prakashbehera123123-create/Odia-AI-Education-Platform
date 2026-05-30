from pathlib import Path

from scripts.utils.path_utils import ensure_dir


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def list_pdfs(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.pdf") if path.is_file())
