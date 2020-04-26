from flask import Flask, render_template, abort
from data import db_session



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='Pycon')


@app.route('/problems/<problem_id>', methods=["GET", "POST"])
def problem(problem_id):
    session = db_session.create_session()
    problem = session.query(Problem).get(problem_id)
    if not problem:
        abort(404)
    return render_template('problem.html',
                           title=f"Задача №{problem_id}")
    


if __name__ == '__main__':
    db_session.global_init("data/database/main.db")
    app.run(port=8080, host='127.0.0.1')
