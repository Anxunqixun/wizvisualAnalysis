from collections import defaultdict
from datetime import datetime, timedelta

import fromServerRemoteMysqlGetInfo as datasources  # 导入数据获取文件
import config as configpy

# 音频附件扩展名
AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma", ".amr", ".opus")


def processData(d):
    QuantificationData = []  # 原始待量化数据
    for a in d:  # 从getData中获取数据
        c, cn = 0, []
        if a["attachInfo"]:
            for m in a["attachInfo"]:
                cn.append([m["name"], m["size"]])
                c += m["size"] or 0
        QuantificationData.append(
            [
                a["name"],
                a["path"],
                a["creatDate"],
                a["wordCount"],
                a["phoCounut"],
                len(a["attachInfo"]),
                c,
                cn,
            ]
        )
    return QuantificationData


def getData():
    db_config = configpy.db_config
    wiz_config = configpy.wiz_config
    wiz = datasources.WizServer(db_config, wiz_config)
    wiz.connectDatabase()
    wiz.sizeCorrect()  # 修正录音数据大小异常
    return processData(wiz.returnInfo())  # 处理数据为量化参数


def _is_audio(name: str) -> bool:
    if not name:
        return False
    lower = name.lower()
    return any(lower.endswith(ext) for ext in AUDIO_EXTS)


def _format_size(num_bytes: int) -> str:
    n = float(num_bytes or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(n)} {unit}"
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"


def _to_date_str(dt) -> str | None:
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    if dt is None:
        return None
    s = str(dt)
    return s[:10] if len(s) >= 10 else s


def buildSummary(raw, marks):
    """汇总：文章数、字数、图片、音频、附件、量化分。"""
    total_articles = len(raw)
    total_words = sum(int(a[3] or 0) for a in raw)
    total_photos = sum(int(a[4] or 0) for a in raw)
    total_attachments = sum(int(a[5] or 0) for a in raw)
    total_attach_size = sum(int(a[6] or 0) for a in raw)

    audio_count = 0
    audio_size = 0
    for a in raw:
        for name, size in a[7] or []:
            if _is_audio(name):
                audio_count += 1
                audio_size += int(size or 0)

    total_score = round(sum(float(m[4] or 0) for m in marks), 3)
    avg_words = round(total_words / total_articles, 1) if total_articles else 0
    avg_score = round(total_score / total_articles, 3) if total_articles else 0

    path_counter = defaultdict(int)
    for a in raw:
        path_counter[a[1] or "未分类"] += 1
    path_top = sorted(
        [{"path": p, "count": c} for p, c in path_counter.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:8]

    return {
        "article_count": total_articles,
        "word_count": total_words,
        "word_count_display": f"{total_words:,}",
        "avg_words": avg_words,
        "photo_count": total_photos,
        "attachment_count": total_attachments,
        "attachment_size": total_attach_size,
        "attachment_size_display": _format_size(total_attach_size),
        "audio_count": audio_count,
        "audio_size": audio_size,
        "audio_size_display": _format_size(audio_size),
        "total_score": total_score,
        "avg_score": avg_score,
        "path_top": path_top,
    }


def buildContribution(raw):
    """按日汇总贡献数据，前端按「最近一年 / 自然年 / 全部」筛选渲染。"""
    by_date = defaultdict(lambda: {"count": 0, "words": 0})
    for a in raw:
        key = _to_date_str(a[2])
        if not key:
            continue
        by_date[key]["count"] += 1
        by_date[key]["words"] += int(a[3] or 0)

    day_map = {
        k: {"count": v["count"], "words": v["words"]}
        for k, v in sorted(by_date.items())
    }
    years = sorted({int(k[:4]) for k in day_map}, reverse=True)
    today = datetime.now().date().strftime("%Y-%m-%d")
    earliest = next(iter(day_map), None)
    latest = today
    if day_map:
        latest = max(max(day_map.keys()), today)

    return {
        "day_map": day_map,
        "years": years,
        "earliest": earliest,
        "latest": latest,
        "today": today,
    }


def getTimeBonusEnhanced(dt):
    """返回时间段加成系数。"""
    if not isinstance(dt, datetime):
        return 1.0
    time_rules = configpy.time_rules
    hour, minute = dt.hour, dt.minute

    for (start_h, start_m), (end_h, end_m), bonus in time_rules:
        if start_h > end_h:
            if (
                (hour > start_h or hour < end_h)
                or (hour == start_h and minute >= start_m)
                or (hour == end_h and minute < end_m)
            ):
                return bonus
        else:
            if (
                (hour > start_h and hour < end_h)
                or (hour == start_h and minute >= start_m)
                or (hour == end_h and minute < end_m)
            ):
                return bonus
    return 1.0


def getPathValueEnhanced(path):
    config = configpy.getPathValueEnhancedconfig
    if path in config:
        return config[path]
    matched_paths = [p for p in config.keys() if path.startswith(p)]
    if matched_paths:
        longest_match = max(matched_paths, key=len)
        return config[longest_match]
    return 1


def quantification(d):
    # d=[name,path,creatDate,wordCount,phoCounut,attachCount,attachSize,attachSizeInfo]
    out = []
    for a in d:
        print(a)
        pde = getPathValueEnhanced(a[1]) + getTimeBonusEnhanced(a[2]) - 1
        config = configpy.quantificationconfig
        wordMark = round(config["word"] * a[3], 5)
        phoMark = config["pho"] * a[4]
        attachMark = config["attach"] * a[5]
        allMark = round((wordMark + phoMark + attachMark) * pde, 3)
        out.append([a[0], wordMark, phoMark, attachMark, allMark])
        print(f"wordMark: {wordMark} phoMark: {phoMark} attachMark: {attachMark} allMark: {allMark}")
    return out


def getQMData():
    """兼容旧接口：仅返回量化分数列表。"""
    return quantification(getData())


def getDashboardData():
    """仪表盘：量化分 + 汇总统计 + 贡献热力图原始日数据。"""
    raw = getData()
    marks = quantification(raw)
    summary = buildSummary(raw, marks)
    contribution = buildContribution(raw)
    return marks, summary, contribution


if __name__ == "__main__":
    print(getQMData())
