from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/cpi')
    def cpi():
        return render_template('index.html')

    @app.route('/ism')
    def ism():
        return render_template('index.html')    

    return app
