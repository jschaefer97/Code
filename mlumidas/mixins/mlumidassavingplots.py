import os
import re
from typing import Any, Dict, List, Union

from matplotlib.figure import Figure


class MLUMidasSavingPlotsMixin:
    """
    Save plot dictionaries produced by:
      - get_oof_plots
      - get_oof_all_periods_plots
      - get_oof_single_quarter_plots

    The directory structure mirrors the nested dictionary structure.
    Each dictionary key becomes a folder; figures are saved as 'plot.<fmt>' at the leaf.
    """

    # ---------- Public API ----------

    def save_plots(
        self,
        plots_dict: Dict[str, Any],
        file_path: str,
        fmt: str = "png",
        dpi: int = 150,
    ) -> List[str]:
        """
        Save all figures found in a nested plot dictionary to disk.

        Args:
            plots_dict: A nested dictionary whose leaves are matplotlib Figure objects.
            file_path:  Root directory where plots should be saved (created if missing).
            fmt:        Image format passed to matplotlib (e.g., "png", "pdf", "svg").
            dpi:        Resolution used by matplotlib when saving raster formats.

        Returns:
            A list of absolute file paths to the saved figure files.
        """
        if not isinstance(plots_dict, dict):
            raise TypeError("plots_dict must be a dictionary")

        saved: List[str] = []
        root = os.path.abspath(file_path)
        self._ensure_dir(root)

        self._save_nested(node=plots_dict, base_dir=root, saved_paths=saved, fmt=fmt, dpi=dpi)
        return saved

    # ---------- Internal helpers ----------

    def _save_nested(
        self,
        node: Any,
        base_dir: str,
        saved_paths: List[str],
        fmt: str,
        dpi: int,
    ) -> None:
        """
        Recursively walk a nested structure of dicts/lists and save Figure leaves.
        Each dict key becomes a subfolder under base_dir.
        """
        if isinstance(node, dict):
            for key, child in node.items():
                folder = os.path.join(base_dir, self._sanitize_key(key))
                self._save_nested(child, folder, saved_paths, fmt, dpi)
            return

        # Optionally handle lists/tuples of figures (not expected, but safe)
        if isinstance(node, (list, tuple)):
            for idx, child in enumerate(node):
                folder = os.path.join(base_dir, f"{idx:03d}")
                self._save_nested(child, folder, saved_paths, fmt, dpi)
            return

        # Leaf: Figure
        if isinstance(node, Figure):
            self._ensure_dir(base_dir)
            out_path = os.path.join(base_dir, f"plot.{fmt.lower()}")
            # Figure objects can be saved even if previously closed
            node.savefig(out_path, dpi=dpi, bbox_inches="tight")
            saved_paths.append(out_path)
            return

        # Unknown leaf type — create folder and drop a README for traceability
        self._ensure_dir(base_dir)
        info_path = os.path.join(base_dir, "README.txt")
        if not os.path.exists(info_path):
            with open(info_path, "w", encoding="utf-8") as f:
                f.write(
                    "This folder corresponds to a leaf in the plot dictionary that "
                    "was not a matplotlib Figure (or list/tuple of Figures).\n"
                )

    @staticmethod
    def _ensure_dir(path: str) -> None:
        """Create a directory if it doesn't exist."""
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def _sanitize_key(key: Union[str, int, float, None]) -> str:
        """
        Convert arbitrary dictionary keys (e.g., periods, timestamps) to safe folder names.
        """
        if key is None:
            s = "None"
        else:
            s = str(key)

        # Replace path separators and trim whitespace
        s = s.strip().replace(os.sep, "_").replace("/", "_").replace("\\", "_")

        # Collapse spaces and disallowed characters
        s = re.sub(r"\s+", "_", s)
        s = re.sub(r"[^A-Za-z0-9._\-+=@]", "_", s)

        # Avoid empty names
        return s or "key"
