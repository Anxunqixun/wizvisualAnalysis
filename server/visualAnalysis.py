from datetime import datetime, timedelta

from flask import Flask, render_template

import config as configpy
import quantitativeModel as qm

# 启动时拉取数据，并记录刷新时间（容器定时重启后会重新执行）
data, summary, contribution = qm.getDashboardData()
refresh_time = datetime.now()
app = Flask(__name__)


@app.route("/")
def index():
    # 下拉与表格展示用中文列名
    headers = ["笔记名称", "字数量化分", "图片量化分", "附件量化分", "综合量化分"]
    interval = configpy.RESTART_INTERVAL_SECONDS
    next_refresh = None
    if interval and interval > 0:
        next_refresh = refresh_time + timedelta(seconds=interval)

    return render_template(
        "index.html",
        data=data,
        summary=summary,
        contribution=contribution,
        headers=headers,
        title="Wiz 量化数据可视化分析",
        refresh_time=refresh_time.strftime("%Y-%m-%d %H:%M:%S"),
        next_refresh=next_refresh.strftime("%Y-%m-%d %H:%M:%S") if next_refresh else None,
        restart_interval_hours=round(interval / 3600, 2) if interval else None,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=configpy.APP_PORT)
