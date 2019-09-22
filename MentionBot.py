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
#Config file
config = None

def loadConfig():
    global config
    #Load configs
    try:
        config = yaml.load(open(os.path.join(os.path.dirname(__file__),'config.yaml')).read(), Loader=yaml.FullLoader)
    except:
        print("'config.yaml' could not be located. Please ensure 'config.example' has been renamed")
        exit()

def saveCache(postCache):
    postCacheName = os.path.join(os.path.dirname(__file__), "cache.json")
    with open(postCacheName, 'w') as fout:
        for chunk in json.JSONEncoder().iterencode(postCache):
            fout.write(chunk)

def loadCache():
    postCache = {}
    postCacheName = os.path.join(os.path.dirname(__file__), "cache.json")
    try:
        with open(postCacheName, 'r') as fin:
            cache = fin.read()
        postCache = json.loads(cache)
    except:
        pass
    return postCache

def postWebhook(webhook, mentions, postCache):
    for comment in mentions:
        try:
            title = 'Posted on {} by {}'.format(comment.subreddit, comment.author)
            description = '[Comment]({})'.format('https://www.reddit.com' + comment.permalink)
            print(title)
            print(description)
            embed = DiscordEmbed(title=title, description=description, color=242424)
            webhook.add_embed(embed)
            webhook.execute()
            webhook.remove_embed(0)
            postCache[comment.id] = comment.permalink
        except:
            pass
    return postCache

if __name__ == '__main__':
    #Initiate a bunch of stuff
    loadConfig()
    api = PushshiftAPI()
    webhook = DiscordWebhook(url=config["webhook"])
    postCache = loadCache()
    #Scan stream of comments to find mentions of word
    try:
        gen = api.search_comments(q='"'+ config['searchString'] + '"', limit=config['maxResults'])
        mentions = []
        for comment in gen:
            if comment.subreddit not in config['subredditsToIgnore'] and comment.id not in postCache:
                if config['searchString'] in comment.body.lower():
                    print("New comment! " + comment.id)
                    mentions.append(comment)
        if mentions:
            postCache = postWebhook(webhook, mentions, postCache)
            saveCache(postCache)
    except:
        pass