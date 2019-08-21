import feedparser

from . import app, db

from flask import render_template, flash, request, redirect, url_for, abort
from models import Podcast, Episode#, User

from tasks import get_feed_info

#from flask.ext.login import login_user, login_requird, logout_user, current_user

@app.route('/')
def index():
    podcasts = Podcast.query.all()
    return render_template('index.html', podcasts=podcasts)

@app.route('/show/', methods=['POST'])
def new_show():
    # TODO: add podcast to database, redirect to stub page
    podcast = Podcast()
    podcast.url = request.form['url']
    podcast.name = request.form['name']

    db.session.add(podcast)
    db.session.commit()

    get_feed_info.delay(podcast.id)

    return redirect(url_for('show', show=podcast.id))

@app.route('/update/<show>')
def update(show):
    return redirect(url_for('show', show=podcast.id))


@app.route('/delete/<show>')
def delete_show(show):
    Podcast.query.filter_by(id=show).delete()
    Episode.query.filter_by(podcast_id=show).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/show/<show>')
def show(show):
    # might be a stub
    # might be complete
    # display relevant info

    podcast = Podcast.query.filter_by(id=show).first()
    if not podcast:
        abort(404)

    edata = [e.get_data() for e in podcast.episodes]

    return render_template('show.html',
                           podcast=podcast,
                           data=podcast.get_data(),
                           edata=edata)


#   @app.route('/login/')
#   def login():
#       if request.method == 'GET':
#           return render_template('login.html')
#       if request.method == 'POST':
#           email = request.form.get('email')
#           password = request.form.get('password')

#           user = User.query.filter_by(email=email, password=password).first()

#           if user:
#               login_user(user)
#               flask.flash('Login successful')

#               return redirect(url_for('index'))
#           else:
#               flash('Login failed')
#               return redirect(url_for('login'))

#   @app.route('/logout/')
#   @login_required
#   def logout():
#       logout_user()
#       return redirect(url_for('index'))
