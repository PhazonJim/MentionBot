import praw
import os
import re
import yaml
from discord_webhook import DiscordWebhook, DiscordEmbed

#===Globals===#
#Reddit PRAW Object
reddit = None
#Config file
config = None
webhook = None

def init():
    global config
    global reddit
    global webhook
    config = yaml.load(open('config.yaml').read())
    client = config['client']
    reddit = praw.Reddit(**client)
    webhook = webhook = DiscordWebhook(url=config["webhook"])

if __name__ == '__main__':
    #Initiate a bunch of stuff
    init()
    #Scan stream of comments to find mentions of word
    for comment in reddit.subreddit(config['subreddit']).stream.comments():
        if re.search(config['regex'], comment.body):
            # create embed object for webhook
            title = 'Posted on {} by {}'.format(comment.subreddit, comment.author.name)
            description = '[Comment]({})'.format('https://www.reddit.com' + comment.permalink)
            embed = DiscordEmbed(title=title, description=description, color=242424)
            webhook.add_embed(embed)
            webhook.execute()
        