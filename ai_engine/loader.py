"""
AI Engine Loader — Dynamic version loader untuk AI_OS.
Memungkinkan switching antar versi AI tanpa restart server.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, List, Optional

from core.config import get_active_version
from core.exceptions import AIVersionNotFoundError
from core.logger import get_logger

logger = get_logger(__name__)


def load_ai(version: Optional[str] = None) -> Any:
    """
    Load AI brain module berdasarkan versi aktif atau versi yang diminta.

    Args:
        version: Versi yang ingin di-load. Jika None, gunakan active version.

    Returns:
        Module brain dari versi yang diminta.

    Raises:
        AIVersionNotFoundError: Jika versi tidak ditemukan.
    """
    target_version = version or get_active_version()
    module_path = f"ai_versions.{target_version}.brain"
    version_dir = Path(f"ai_versions/{target_version}")

    if not version_dir.exists():
        raise AIVersionNotFoundError(
            f"Versi {target_version} tidak ditemukan di {version_dir}"
        )

    try:
        module = importlib.import_module(module_path)
        # Reload module setiap kali agar membaca konfigurasi / env terbaru
        module = importlib.reload(module)
        logger.info(f"Berhasil load AI version: {target_version} (reloaded)")
        return module
    except ImportError as e:
        logger.error(f"Gagal import module {module_path}: {e}")
        raise AIVersionNotFoundError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error loading {module_path}: {e}")
        raise AIVersionNotFoundError(str(e))


def get_available_versions() -> List[str]:
    """Scan dan return semua versi AI yang tersedia."""
    versions_dir = Path("ai_versions")
    try:
        return sorted(
            [
                d.name
                for d in versions_dir.iterdir()
                if d.is_dir() and d.name.startswith("v")
            ]
        )
    except Exception as e:
        logger.error(f"Failed scanning versions: {e}")
        return []

