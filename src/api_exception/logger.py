import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("api_exception")

# If the user has not set a level (default is NOTSET), set it to WARNING
if logger.level == logging.NOTSET:
    logger.setLevel(logging.WARNING)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def add_file_handler(path: str, level=logging.INFO):
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(level)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# -------- NEW: structured log helper (formatı bozmadan meta’yı ekrana basar) --------

# LogRecord üzerinde rezervli anahtarlar: bunları extra'da aynen kullanamayız
_RESERVED_KEYS = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module",
    "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs",
    "relativeCreated", "thread", "threadName", "processName", "process", "message", "asctime"
}


def _sanitize_extra(meta: Dict[str, Any]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for k, v in meta.items():
        key = k if k not in _RESERVED_KEYS else f"meta_{k}"
        try:
            json.dumps(v, ensure_ascii=False, default=str)
            safe[key] = v
        except Exception:
            safe[key] = str(v)
    return safe


# ---- görselleştirme ayarları ----
META_STYLE = "kv_block"  # "kv_block" | "pretty_json"
META_SORT_KEYS = False  # anahtarları alfabetik sırala
META_MAX_VAL_LEN = 200  # tek satırda bu uzunluğu aşan value'ları kısalt
META_INDENT = 2  # pretty_json için girinti


def _shorten(s: str, limit: int = META_MAX_VAL_LEN) -> str:
    if len(s) <= limit:
        return s
    return s[: max(0, limit - 3)] + "..."


def _fmt_kv_block(meta: Dict[str, Any]) -> str:
    items = list(meta.items())
    if META_SORT_KEYS:
        items.sort(key=lambda kv: str(kv[0]))
    # anahtar genişliği
    width = min(40, max((len(str(k)) for k, _ in items), default=0))
    lines = []
    for k, v in items:
        try:
            if isinstance(v, (dict, list, tuple)):
                v_str = json.dumps(v, ensure_ascii=False, default=str)
            else:
                v_str = str(v)
        except Exception:
            v_str = repr(v)
        v_str = _shorten(v_str, META_MAX_VAL_LEN)
        lines.append(f"│ {str(k):<{width}} : {v_str}")
    return "\n".join(lines)


def _fmt_pretty_json(meta: Dict[str, Any]) -> str:
    try:
        s = json.dumps(meta, ensure_ascii=False, indent=META_INDENT, sort_keys=META_SORT_KEYS, default=str)
    except Exception:
        s = json.dumps({k: str(v) for k, v in meta.items()}, ensure_ascii=False, indent=META_INDENT,
                       sort_keys=META_SORT_KEYS)
    return s


def _format_meta(meta: Dict[str, Any]) -> str:
    if META_STYLE == "pretty_json":
        return _fmt_pretty_json(meta)
    return _fmt_kv_block(meta)  # default kv_block


def log_with_meta(level: int, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """
    1) Mevcut formatter ile ana mesajı yazar (structured context 'extra' içinde taşınır)
    2) Aynı formatter ile, alt satırda okunaklı bir 'meta' bloğu basar (çok satırlı)
    """
    if not meta:
        logger.log(level, message)
        return

    # Line 1: original message + structured extra
    safe_extra = _sanitize_extra(meta)
    logger.log(level, message, extra=safe_extra)

    # Line 2: meta block with a required lines
    block = _format_meta(meta)
    logger.log(level, "meta:\n%s", block)
