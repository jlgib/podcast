"""Provide a local cache of subscribed content."""


import os
import re
import requests

from . import config

CONFIG = config.Config()


def download_episode(url, show_id, episode_id):
    req = requests.get(url)

    cd = req.headers['content-disposition']
    match = re.findall('filename="(.+)"', cd)
    if match:
        original_fname = match[0]
    else:
        original_fname = os.path.basename(url)

    local_fname = '{episode_id}_{original_fname}'.format(
            episode_id=episode_id, original_fname=original_fname)

    show_dir = os.path.join(CONFIG['CACHE_DIR'], str(podcast_id))
    if not os.path.exists(show_dir):
        os.makedirs(show_dir)

    target = os.path.join(show_dir, local_fname)
    with open(target, 'wb') as fh:
        fh.write(req.content)

    return target
