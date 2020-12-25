from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, UserMixin, LoginManager, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
import os

application = Flask(__name__)
application.config.from_object('configuration.DevelopmentConfig')
database = SQLAlchemy(application)
manager = LoginManager(application)


class TagLeaders(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.Text, nullable=False)
    user = database.Column(database.Text, nullable=False, unique=True)
    password = database.Column(database.Text, nullable=False)
    moves = database.Column(database.Integer, nullable=False)
    wintime = database.Column(database.Integer, nullable=False)


@application.route('/about')
def index():
    return render_template('index.html')


@application.route('/leaderboard')
def leaderboard():
    users = database.session.query(TagLeaders).filter(TagLeaders.moves != 9999,
                                                      TagLeaders.wintime != 9999).order_by(
        TagLeaders.moves.asc(), TagLeaders.wintime.asc()).limit(10).all()
    return render_template('leaderboard.html', users=users)


@application.route('/user/login', methods=['GET', 'POST'])
def sign_in():
    login = request.form.get('login')
    password = request.form.get('password')
    user = database.session.query(TagLeaders).filter_by(user=f'users@{login}').first()
    if request.method == 'POST':
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html')


@application.route('/user/register', methods=['GET', 'POST'])
def sign_up():
    name = request.form.get('name')
    login = f"users@{request.form.get('login')}"
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if request.method == 'POST':
        if password != password2:
            print('ggg')
        else:
            hash_password = generate_password_hash(password)
            new_user = TagLeaders(username=name, user=login, password=hash_password, moves=9999, wintime=9999)
            database.session.add(new_user)
            database.session.commit()
            return redirect(url_for('sign_in'))
    return render_template('register.html')


@application.route('/user/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('sign_in'))


@application.route('/game', methods=['GET', 'POST'])
@login_required
def taggame():
    moves = request.form.get('moves')
    time = request.form.get('time')
    user = database.session.query(TagLeaders).filter_by(id=current_user.id).first()
    if request.method == 'POST':
        if int(moves) <= user.moves:
            user.wintime = int(time)
            user.moves = int(moves)
            database.session.commit()
        return redirect(url_for('leaderboard'))
    return render_template('taggame.html')


@application.route('/')
def redirect_to_the_index():
    return redirect(url_for('index'))


@manager.user_loader
def load_user(user_id):
    return database.session.query(TagLeaders).get(user_id)


@application.after_request
def redirect_to_sign_in(response):
    if response.status_code == 401:
        return redirect(url_for('sign_in') + '?next=' + request.url)
    return response


@application.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(application.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == '__main__':
    application.run()
