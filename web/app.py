import firebase_admin
from flask import Flask, render_template
from firebase_admin import credentials
from firebase_admin import db

app = Flask(__name__)


# Firebase database 인증 및 앱 초기화
cred = credentials.Certificate('../mykey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://breaker-a66d4-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


@app.route('/')
def home():
    return render_template('bar.html')


@app.route('/corr')
def bar():
    return render_template('index.html')


@app.route("/<string:indicator>", methods=['GET'])
def chart(indicator):
    return render_template("chart.html", indicator=indicator)


@app.route('/api/snp/')
def stock_data():
    ref = db.reference()
    data = ref.child('S&P500').get()
    return data


@app.route('/api/indicator/')
def indi_data():
    ref = db.reference()
    data = ref.child('Indicator').get()
    return data


@app.route('/api/')
def api_data():
    ref = db.reference()
    data = []
    temp1 = ref.child('spy').get()
    temp2 = ref.child('ssec').get()
    temp3 = ref.child('stoxx').get()
    data.append(temp1)
    data.append(temp2)
    data.append(temp3)
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

