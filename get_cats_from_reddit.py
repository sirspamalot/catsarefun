#!/usr/bin/env python3

import glob
import requests
import random
import os
import sys
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
GFYCAT = "https://api.gfycat.com/v1/gfycats/{}"

headers = {"user-agent": "reddit-{}".format(os.environ.get("USER", "cse-20289-sp19"))}


def dl_content(url, source):
    if source == "gfycat.com":
        gfy_url = url.split("/")[-1]

        r = requests.get(GFYCAT.format(gfy_url)).json()
        gfy_mp4url = r["gfyItem"]["mp4Url"]

        return gfy_mp4url

    elif source == "i.imgur.com":
        img_url = url.replace(".gifv", ".mp4")
        return img_url

    else:
        return url


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
    return dl_content(*img[:-1]), img[-1]


def write_file(img_url, title):
    if not img_url:
        sys.stderr.write("Something went wrong - no url\n")
        return

    parse = urlparse(img_url)
    if parse.netloc == 'v.redd.it':
        sys.stderr.write(
            "The source of this file is v.redd.it. Unfortunately, reddit recognizes requests to this source as being from a script and blocks them. Apologies.\n"
        )
        return

    ext = parse.path.split('.', 1)[-1]
    if not ext in ("mp4", "png", "gif", "jpeg", "jpg"):
        print("can't handle url {}".format(img_url),
              file=sys.stderr)
        return

    # remove former cat file, necessary for applescript
    for cat_file in glob.glob("cat*"):
        os.unlink(cat_file)

    fname = "cat." + ext
    r = requests.get(img_url, stream=True)

    # Print title for text msg
    print("Title: {}".format(title))

    with open(fname, "wb") as file:
        file.write(r.content)


img, title = handle_url()
write_file(img, title)
