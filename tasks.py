import os
import re
import logging

from celery import Celery
import feedparser
import requests

from models import Podcast, Episode

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def get_feed_info(podcast_id):
    logging.toaster()
    podcast = Podcast.query.filter_by(id=podcast_id).first()
    feed = feedparser.parse(podcast.url)
    podcast.set_data(feed['feed'])
    db.session.add(podcast)
    db.session.commit()

    # add episodes too while we have the feed pulled:

    # only add new episodes. maybe per-show uniqueness eventually?
    episode_ids = [e.episode_id for e in podcast.episodes]
    for episode_data in feed['entries']:
        if episode_data['id'] in episode_ids:
            # update existing entry
            pass
        else:
            episode = Episode()
            episode.title = episode_data['title']
            episode.episode_id = episode_data['id']
            episode.set_data(episode_data)
            episode.podcast_id = podcast.id
            db.session.add(episode)

    cache_episodes.delay(podcast_id)

@app.task
def cache_episode(url, podcast_id, episode_id):
    req = requests.get(url)

    cd = req.headers['content-disposition']
    match = re.findall('filename="(.+)"', cd)
    if match:
        original_fname = match[0]
    else:
        original_fname = os.path.basename(url)

    local_fname = '{episode_id}_{original_fname}'.format(
            episode_id=episode_id, original_fname=original_fname)

    show_dir = os.path.join(CACHE_DIR, str(podcast_id))
    if not os.path.exists(show_dir):
        os.makedirs(show_dir)

    target = os.path.join(show_dir, local_fname)
    with open(target, 'wb') as fh:
        fh.write(req.content)

    logging.warn('Grabbing %s', target)
    episode = Episode.query.filter_by(
            id=episode_id, podcast_id=podcast_id).first()
    episode.set_cached_path(target)


@app.task
def cache_episodes(podcast_id):
    podcast = Podcast.query.filter_by(id=podcast_id).first()
    missing = [ep for ep in podcast.episodes if not ep.cached_path]
    # don't fork this, we don't want to spam servers with downloads
    for ep in missing:
        ep.cache()
