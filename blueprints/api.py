from flask import Blueprint, request
from flask_login import login_required, current_user
from data import db_session
from data.models.news import News

blueprint = Blueprint('api', __name__)


@login_required
@blueprint.route('/rate_news', methods=["POST"])
def rate_news():
    news_id, rate = request.json.get("news_id"), request.json.get("rate")

    if not news_id or rate not in [-1, 1]:
        return

    session = db_session.create_session()

    news = session.query(News).get(news_id)
    if not news:
        return

    current_user.rate_news(news, rate)
    return {"status": "OK", "new_rating": news.rating}


@login_required
@blueprint.route('/unrate_news', methods=["POST"])
def unrate_news():
    news_id = request.json.get("news_id")

    if not news_id:
        return

    session = db_session.create_session()

    news = session.query(News).get(news_id)
    if not news:
        return

    current_user.unrate_news(news)
    return {"status": "OK", "new_rating": news.rating}
