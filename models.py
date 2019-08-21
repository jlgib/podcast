import json

from flask_app import app, db, config#, bcrypt
# from tasks import cache_episode

# from flask.ext.login import UserMixin
# from sqlalchemy.ext.hybrid import hybrid_property

import cache


class Podcast(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    url = db.Column(db.String(), nullable=False)
    name = db.Column(db.String())
    data_json = db.Column(db.String())
    episodes = db.relationship('Episode',
                               backref='podcast',
                               passive_deletes=True)

    def get_data(self):
        if not self.data_json:
            return None
        return json.loads(self.data_json)

    def set_data(self, data_json):
        self.data_json = json.dumps(data_json,
                default=lambda o: '<not serializable>')


class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    podcast_id = db.Column(
            db.Integer, db.ForeignKey('podcast.id', ondelete='CASCADE'))
    data_json = db.Column(db.String())

    # if unset, we have not cached it to disk yet:
    cached_path = db.Column(db.String())

    # if unset, we have not parsed & cached this value from the data yet:
    media_links = db.Column(db.ARRAY(db.String()))

    # common attributes we want indexed:
    episode_id = db.Column(db.String())

    def get_data(self):
        if not self.data_json:
            return None
        return json.loads(self.data_json)

    def set_data(self, data_json):
        self.data_json = json.dumps(data_json,
                default=lambda o: '<not serializable>')

    def cached_media_links(self):
        """parse and set media links from data."""
        if not self.media_links:
            links = self.get_data()[u'links']
            if links:
                media_links = [l[u'href'] for l in links
                               if l[u'type'].startswith(u'audio')]
                if media_links:
                    self.media_links = media_links
                    db.session.add(self)
                    db.session.commit()
        return self.media_links

    def cache(self):
        if not self.cached_path:
            media_links = self.cached_media_links()
            if media_links:
                cached_path = cache.download_episode(
                        media_links[0], self.podcast_id, self.id)

                self.cached_path = cached_path
                db.session.add(self)
                db.session.commit()


#   class User(db.Model, UserMixin):
#       id = db.Column(db.Integer, primary_key=True)

#       email = db.Column(db.String(80), unique=True)
#       _password = db.Column(db.String(80))

#       def __init__(self, email, password):
#           self.email = email
#           self._set_password(password)

#       @hybrid_property
#       def password(self):
#           return self._password

#       @password.setter
#       def _set_password(self, plaintext):
#           self._password = bcrypt.generate_password_hash(plaintext)




db.create_all()
