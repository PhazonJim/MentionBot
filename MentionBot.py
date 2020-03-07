from psaw import PushshiftAPI
import os
import re
import yaml
import json
import time
import textwrap
from pprint import pprint
from discord_webhook import DiscordWebhook, DiscordEmbed

#===Constants===#
CONFIG_FILE = os.path.join(os.path.dirname(__file__),"config.yaml")
CACHE_FILE =  os.path.join(os.path.dirname(__file__), "cache.json")

#===Globals===#
#Config file
config = None

def loadConfig():
    global config
    try:
        config = yaml.load(open(CONFIG_FILE).read(), Loader=yaml.FullLoader)
    except:
        print("'config.yaml' could not be located. Please ensure 'config.example' has been renamed")
        exit()

def loadCache():
    postCache = {"comments":{}, "submissions":{}}
    try:
        with open(CACHE_FILE, "r") as fin:
            postCache = json.load(fin)
    except Exception as e:
        print (e)
    return postCache

def saveCache(postCache):
    with open(CACHE_FILE, "w") as fout:
        for chunk in json.JSONEncoder().iterencode(postCache):
            fout.write(chunk)

def postWebhook(webhook, item, postCache, mentionType):
    try:            
        title = "Posted on {} by {}".format(item.subreddit, item.author)
        embed = None
        if mentionType == "comments":
            description = "[Comment Permalink]({})".format("https://www.reddit.com" + item.permalink + "?context=10000")
            embed = DiscordEmbed(title=title, description=description, color=242424)
            embed.add_embed_field(name="Comment Preview:", value=textwrap.shorten(item.body, width=900, placeholder="...(Too long to preview full content)..."))
        elif mentionType == "submissions":
            description = "[Submission Permalink]({})".format("https://www.reddit.com" + item.permalink)
            embed = DiscordEmbed(title=title, description=description, color=242424)
            embed.add_embed_field(name="Submission Title:", value=item.title)
            embed.add_embed_field(name="Submission Preview:", value=textwrap.shorten(item.selftext, width=900, placeholder="...(Too long to preview full content)...") if item.selftext else "Submission is a direct link")
        webhook.add_embed(embed)
        webhook.execute()
        webhook.remove_embed(0)
        postCache[mentionType][item.id] = item.permalink
    except Exception as e:
        print(e)
        pass
    return postCache

def queryPushshift(api, postCache, queryType):
    try:
        gen = None
        mentions = []
        if queryType == "comments":
            gen = api.search_comments(q='"'+ config["searchString"] + '"', limit=config["maxResults"])
        elif queryType == "submissions":
            gen = api.search_submissions(q='"'+ config["searchString"] + '"', limit=config["maxResults"])
        for item in gen:
            if item.subreddit not in config["subredditsToIgnore"]:
                if queryType == "comments" and item.id not in postCache["comments"]:
                    if config["searchString"] in item.body.lower():
                        mentions.append(item)
                if queryType == "submissions" and item.id not in postCache["submissions"]:
                    if config["searchString"] in item.selftext.lower() or config["searchString"] in item.title.lower():
                        mentions.append(item)
        return mentions
    except Exception as e:
        print(e)
        pass

if __name__ == "__main__":
    #Initiate a bunch of stuff
    loadConfig()
    api = PushshiftAPI()
    webhook = DiscordWebhook(url=config["webhook"])
    postCache = loadCache()
    #Scan stream of comments to find mentions of word
    commentMentions = queryPushshift(api, postCache, "comments")
    for comment in commentMentions:
        postCache = postWebhook(webhook, comment, postCache, "comments")
        time.sleep(3)
    #Scan stream of submissions to find mentions of word
    submissionMentions = queryPushshift(api, postCache, "submissions")
    for submission in submissionMentions:
        postCache = postWebhook(webhook, submission, postCache, "submissions")
        time.sleep(3)
    if postCache:
        saveCache(postCache)
