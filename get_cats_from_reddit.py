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


def write_file(img_url, title):
    if not img_url:
        sys.stderr.write("Something went wrong - no url\n")
        return

    parse = urlparse(img_url)
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


def main():
    img, title = handle_url()
    write_file(img, title)


if __name__ == "__main__":
    main()
