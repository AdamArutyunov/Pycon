from Pycon import permission_required
from flask import Blueprint, render_template, abort, redirect
from flask_login import current_user
from data import db_session
from data.models.news import News
from forms.create_news import *
from lib.Permissions import *

blueprint = Blueprint('news', __name__, template_folder='/templates/news')


@blueprint.route('/create', methods=["GET", "POST"])
@permission_required(Permissions.NEWS_CREATE)
def create_news():
    session = db_session.create_session()
    form = CreateNewsForm()

    if form.validate_on_submit():
        news = News()
        news.author = current_user
        news.title = form.title.data
        news.body = form.body.data

        session.add(news)
        session.commit()

        return redirect('../..')

    return render_template('news/create_news.html', title="Опубликовать новость",
                           form=form, action="Опубликовать")


@blueprint.route('/<int:news_id>/edit', methods=["GET", "POST"])
@permission_required(Permissions.NEWS_EDIT)
def edit_news(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404)

    form = CreateNewsForm()
    if form.validate_on_submit():
        news.title = form.title.data
        news.body = form.body.data

        session.commit()

        return redirect(f'../..')

    form.title.data = news.title
    form.body.data = news.body

    return render_template('news/create_news.html', title=f'Редактирование новости №{news.id}',
                           form=form, action="Сохранить")


@blueprint.route('/<int:news_id>/delete')
@permission_required(Permissions.NEWS_DELETE)
def delete_news(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)

    if not news:
        abort(404)

    session.delete(news)
    session.commit()

    return redirect('../..')
