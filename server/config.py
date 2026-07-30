"""从环境变量 / .env 加载全部运行配置。"""
import json
import os

from dotenv import load_dotenv

# 本地开发时读取项目根目录 .env；Docker 中由 compose 注入环境变量
load_dotenv()


def _env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key)
    if value is None or value == "":
        return default
    return value


def _env_int(key: str, default: int) -> int:
    value = _env(key)
    if value is None:
        return default
    return int(value)


def _env_float(key: str, default: float) -> float:
    value = _env(key)
    if value is None:
        return default
    return float(value)


def _env_json(key: str, default):
    raw = _env(key)
    if raw is None:
        return default
    return json.loads(raw)


# ---------- 时间段加成：[[开始时, 开始分], [结束时, 结束分], 倍率] ----------
# 例如：[[[22, 0], [3, 0], 1.2], [[8, 0], [9, 0], 1.1]]
_time_rules_raw = _env_json(
    "TIME_RULES",
    [[[22, 0], [3, 0], 1.2], [[8, 0], [9, 0], 1.1]],
)
time_rules = [
    (tuple(start), tuple(end), float(bonus))
    for start, end, bonus in _time_rules_raw
]

# ---------- 路径加成字典 ----------
getPathValueEnhancedconfig = _env_json(
    "PATH_BONUS",
    {
        "/My Journals/": 1.2,
        "/My Notes/": 1.4,
    },
)

# ---------- 量化分值参数 ----------
quantificationconfig = {
    "word": _env_float("QUANT_WORD", 0.01),
    "pho": _env_float("QUANT_PHO", 2.0),
    "attach": _env_float("QUANT_ATTACH", 3.0),
}

# ---------- MySQL ----------
db_config = {
    "host": _env("DB_HOST", "localhost"),
    "database": _env("DB_NAME", "wizksent"),
    "user": _env("DB_USER", "root"),
    "password": _env("DB_PASSWORD", ""),
    "port": _env_int("DB_PORT", 3306),
}

# ---------- 为知笔记 Web API ----------
wiz_config = {
    "server": _env("WIZ_SERVER", "http://localhost:80"),
    "author": _env("WIZ_AUTHOR", ""),
    "username": _env("WIZ_USERNAME", ""),
    "password": _env("WIZ_PASSWORD", ""),
}

# ---------- 服务端口（本地 python visualAnalysis.py 时使用）----------
APP_PORT = _env_int("APP_PORT", 5674)

# ---------- 容器/数据定时刷新间隔（秒）；0 表示不展示下次刷新预估 ----------
RESTART_INTERVAL_SECONDS = _env_int("RESTART_INTERVAL_SECONDS", 86400)
