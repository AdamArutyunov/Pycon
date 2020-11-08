from flask import Flask, render_template

app = Flask(__name__)


@app.errorhandler(404)
def under_construction(error):
    return render_template("under_construction.html")


if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0')
