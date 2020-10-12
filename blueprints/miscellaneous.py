from Pycon import permission_required
from flask import Blueprint, render_template, redirect, request
from flask_login import current_user, login_required, login_user, logout_user
from data import db_session
from data.models.news import *
from data.models.user import *
from data.models.group import *
from forms.feedback import *
from forms.register import *
from forms.login import *
from lib.Roles import *

blueprint = Blueprint('miscellaneous', __name__, template_folder='/templates')


@blueprint.route('/')
@permission_required(Permissions.INDEX_VIEW)
def index():
    session = db_session.create_session()
    news = session.query(News).order_by(News.publication_date.desc()).all()

    return render_template('index.html', title='Pycon', news=news)


@blueprint.errorhandler(404)
def not_found(error):
    return render_template('html_error.html', title="404", error_id="404",
                           message='Такой страницы нет! Но есть много других.')


@blueprint.errorhandler(403)
def forbidden(error):
    return render_template('html_error.html', title="403", error_id="403",
                           message='Вам сюда нельзя!')


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    session = db_session.create_session()
    form.group.choices += [(group.id, group.name) for group in session.query(Group).all()]

    if form.validate_on_submit():
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('user/register.html', title='Регистрация',
                                   form=form,
                                   message="Этот логин занят.")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('user/register.html', title='Регистрация',
                                   form=form,
                                   message="Эта почта занята.")
        user = User()
        user.login = form.login.data
        user.email = form.email.data
        user.group = session.query(Group).get(form.group.data)
        user.role = UserRole.id
        user.set_password(form.password.data)

        session.add(user)
        session.commit()

        login_user(user)

        return redirect('/')

    return render_template('user/register.html', title='Регистрация', form=form)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter((User.email == form.login_or_email.data) |
                                          (User.login == form.login_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data, duration=datetime.timedelta(days=7))
            return redirect(request.args.get('next') or '/')
        return render_template('user/login.html',
                               message="Неправильный логин или пароль.",
                               form=form)

    return render_template('user/login.html', title='Авторизация', form=form)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or '/')


@blueprint.route('/feedback', methods=["GET", "POST"])
@permission_required(Permissions.FEEDBACK_LEAVE)
def feedback():
    form = FeedbackForm()

    if form.validate_on_submit():
        body = form.body.data
        contact = form.response_contact.data
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        message = ""
        message += "От: " + (current_user.login if current_user.is_authenticated else "аноним") + "\n\n"
        message += body + "\n\n"

        if contact:
            message += "Контакт для связи: " + contact

        with open(f"temp/feedback/feedback_{timestamp}.txt", "w") as f:
            f.write(message)

        return redirect("/")

    return render_template("feedback.html", title="Обратная связь", form=form)