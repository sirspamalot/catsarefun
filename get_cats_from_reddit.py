#!/usr/bin/env python3

import requests
import random
import os
import sys
from contextlib import suppress
from urllib.parse import urlparse

SUBREDDITS = [
    "cats",
    "catsstandingup",
    "catslaps",
    "catsareassholes",
    "chonkers",
    "bigcatgifs",
    "babybigcatgifs",
    "holdmycatnip",
    "CatsISUOTTATFO",
    "catsareliquid",
]

REDDIT_URL = "https://reddit.com/r/{}/.json?sort=top"

headers = {"user-agent": "reddit-{}".format(os.environ.get("USER", "cse-20289-sp19"))}


def dl_gfycat(url):
    gfy_url = url.split("/")[-1]
    gfycat = "https://api.gfycat.com/v1/gfycats/{}".format(gfy_url)
    r = requests.get(gfycat).json()
    gfy_mp4url = r["gfyItem"]["mp4Url"]
    return gfy_mp4url


def dl_imgur(url):
    img_url = url.replace(".gifv", ".mp4")
    return img_url


def dl_vreddit(url):
    print('The source of this file is v.redd.it. Unfortunately, reddit'
          ' recognizes requests to this source as being from a script and'
          ' blocks them. Apologies.', file=sys.stderr)
    sys.exit(127)


def dl_convert(url, source):
    conv = {
        'gfycat.com'  : dl_gfycat,
        'i.imgur.com' : dl_imgur,
        'v.redd.it' : dl_vreddit,
    }
    fkt = conv.get(source, lambda x: x)
    return fkt(url)


def handle_url(url=REDDIT_URL):
    subreddit = random.choice(SUBREDDITS)
    url = url.format(subreddit)
    response = requests.get(url, headers=headers).json()
    data = response["data"]["children"]
    images = []

    for post in data:
        ctx = post.get('data')
        if ctx["stickied"]:
            continue
        src = ctx['url'], ctx['domain'], ctx['title']
        images.append(src)

    img = random.choice(images)
    return dl_convert(*img[:-1]), img[-1]


def write_file(img_url):

    if not img_url:
        raise ValueError("Something went wrong - no url")

    parse = urlparse(img_url)
    ext = parse.path.split('.', 1)[-1]
    if not ext in ("mp4", "png", "gif", "jpeg", "jpg"):
        raise ValueError("can't handle url {}".format(img_url))

    fname = "cat." + ext
    with open(fname, 'wb') as file:
        r = requests.get(img_url, stream=True)
        file.write(r.content)
    return fname


def main():

    link = 'lastpicture'
    img, title = handle_url()

    # remove former cat file, necessary for applescript
    with suppress(FileNotFoundError):
        lastpic = os.readlink(link)
        os.unlink(lastpic)
        os.unlink(link)

    try:
        out = write_file(img)
        os.symlink(out, link)
    except ValueError as err:
        print(str(err), file=sys.stderr)
    else:
        # Print title for text msg
        print("Title: {}".format(title))


if __name__ == "__main__":
    main()
