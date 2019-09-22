import praw
from psaw import PushshiftAPI
import os
import re
import yaml
import json
import time
from pprint import pprint
from discord_webhook import DiscordWebhook, DiscordEmbed

#===Globals===#
#Reddit PRAW Object
reddit = None
#Config file
config = None
webhook = None
api = None
postCache = None

def init():
    global config
    global reddit
    global webhook
    global api
    global postCache

    #Load configs
    config = yaml.load(open('config.yaml').read())
    client = config['client']

    #Set up APIs
    reddit = praw.Reddit(**client)
    api = PushshiftAPI()
    webhook = webhook = DiscordWebhook(url=config["webhook"])
    
    #Load post cache
    postCacheName = os.path.join(os.path.dirname(__file__), "cache.json")
    with open(postCacheName, 'r') as fin:
        cache = fin.read()
    postCache = json.loads(cache)

def saveCache():
    postCacheName = os.path.join(os.path.dirname(__file__), "cache.json")
    with open(postCacheName, 'w') as fout:
        for chunk in json.JSONEncoder().iterencode(postCache):
            fout.write(chunk)

def postWebhook(mentions):
    for comment in mentions:
        title = 'Posted on {} by {}'.format(comment.subreddit, comment.author)
        description = '[Comment]({})'.format('https://www.reddit.com' + comment.permalink)
        embed = DiscordEmbed(title=title, description=description, color=242424)
        webhook.add_embed(embed)
        webhook.execute()
        webhook.remove_embed(0)
        postCache[comment.id] = comment.permalink
        time.sleep(3)

if __name__ == '__main__':
    #Initiate a bunch of stuff
    init()
    #Scan stream of comments to find mentions of word
    try:
        gen = api.search_comments(q='"'+ config['searchString'] + '"', limit=50)
        mentions = []
        for comment in gen:
            if comment.subreddit != config['ignore'] and comment.id not in postCache:
                if config['searchString'] in comment.body.lower():
                    print("New comment! " + comment.id)
                    mentions.append(comment)
        if mentions:
            postWebhook(mentions)
            saveCache()
    except:
        pass