"""Regenera el catálogo Excel descargable desde la landing.

Uso:  python scripts/build_catalog.py
Ejecutar cada vez que cambie app/content.py (el test test_catalog lo verifica en CI).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.catalog import build_catalog  # noqa: E402

if __name__ == "__main__":
    print(f"Catálogo generado: {build_catalog()}")
