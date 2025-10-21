import os
import pickle
from pathlib import Path
from typing import Any, Optional
from loguru import logger


class CachingMixin:
    """
    Dead-simple per-stage pickle cache used for 'nowdata' and 'varselect'.
    - Each stage saves/loads one pickle at: {file_path_pipelinecache}/{stage}.pkl
    - No signatures or auto invalidation.
      If you change inputs for a stage, include it in `pipelines_to_run` to force a re-run.
    """

    # NOWPipeline.__init__ must set:
    #   self.file_path_pipelinecache = f"{file_path}/cache/pipelinecache"

    def _cache_root(self) -> Path:
        root = Path(self.file_path_pipelinecache)
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _stage_cache_path(self, stage: str) -> Path:
        return self._cache_root() / f"{stage}.pkl"

    def _save_stage_cache(self, stage: str, payload: Any) -> None:
        """Save any picklable object atomically."""
        path = self._stage_cache_path(stage)
        tmp = path.with_suffix(".pkl.tmp")
        with open(tmp, "wb") as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)

    def _load_stage_cache(self, stage: str) -> Optional[Any]:
        """Load pickled object if present; else None. Corrupt -> None."""
        path = self._stage_cache_path(stage)
        if not path.exists():
            return None
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None

    def _has_stage_cache(self, stage: str) -> bool:
        return self._stage_cache_path(stage).exists()
        
    @staticmethod
    def _run_stage_obj(obj: Any) -> None:
        width = 70
        obj_name = obj.__class__.__name__

        border = "═" * (width - 2)
        empty_line = "║" + " " * (width - 2) + "║"
        title_line = f" Running stage {obj_name} in NOWPipeline ".center(width - 2)
        name_line = f" {obj_name} ".center(width - 2)

        logger.info("")
        logger.info(f"╔{border}╗")
        logger.info(empty_line)
        logger.info(f"║{title_line}║")
        logger.info(empty_line)
        logger.info(f"║{name_line}║")
        logger.info(empty_line)
        logger.info(f"╚{border}╝")
        logger.info("")

        if hasattr(obj, "run"):
            obj.run()
        elif hasattr(obj, "process_mapping"):
            obj.process_mapping()
        else:
            raise RuntimeError(f"{obj_name} needs run() or process_mapping().")
