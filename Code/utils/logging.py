# utils/logging.py
import logging
import os
from datetime import datetime
import functools
import time
import sys

def setup_logging(debug: bool = False):
    """
    Configure the cozy_animator logger with:
    - Console: INFO (or DEBUG if debug=True)
    - File: always full DEBUG level, daily rotation
    """
    logger = logging.getLogger("cozy_animator")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove any existing handlers to avoid duplicates on re-config
    logger.handlers.clear()

    # Common formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler — respects debug mode
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG if debug else logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler — always full detail for our records
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(log_dir, f"cozy_animator_{today}.log")
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def log_call(func):
    """
    Gentle decorator that logs function entry/exit + duration.
    Only logs DEBUG when debug mode is actually active.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("cozy_animator")
        
        # Only do debug logging if enabled (respects current level perfectly)
        if logger.isEnabledFor(logging.DEBUG):
            func_name = func.__name__
            # Short arg summary: type for positional, name=… for kwargs
            arg_parts = [type(a).__name__ for a in args[1:]]  # skip self for methods
            for k, v in kwargs.items():
                val_repr = "…" if isinstance(v, (str, list, dict, tuple)) and len(str(v)) > 40 else repr(v)
                arg_parts.append(f"{k}={val_repr}")
            arg_str = ", ".join(arg_parts) if arg_parts else ""
            
            logger.debug(f"→ {func_name}({arg_str})")

        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            
            if logger.isEnabledFor(logging.DEBUG):
                res_repr = "…" if isinstance(result, (list, dict)) and len(str(result)) > 60 else repr(result)
                logger.debug(f"← {func_name} → {res_repr} ({duration:.3f}s)")
            
            return result
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error(f"{func_name} raised {type(e).__name__} after {duration:.3f}s", exc_info=True)
            raise

    return wrapper