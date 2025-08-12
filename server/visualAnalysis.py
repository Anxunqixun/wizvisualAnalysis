from flask import Flask, render_template
import quantitativeModel as qm
data = qm.getQMData() # 获取数据
app = Flask(__name__)

@app.route('/')
def index():
    headers = ['name', 'wordMark', 'phoMark', 'attachMark', 'ultMark']# 列名
    return render_template('index.html', data=data, headers=headers, title="Wiz量化数据可视化分析")
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)