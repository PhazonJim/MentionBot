# RemovalReasonBot
A reddit bot for finding comments containing specific key phrases and notifying a discord webhook

# environment setup instructions
1. Install Python 3
2. Install PIP (https://pip.pypa.io/en/stable/installing/)
3. pip install -r requirements.txt

# Configurations
1. Fill in values for keys in config.example
2. Rename config.example to config.yaml

# Usage
1. Define a string to look for in reddit comments fetched from pushshift
2. Notify Discord server via webhook of the comment

# Features
1. Fetches last X comments (configured in config.yaml) and caches ids to avoid notifying multiple times for the same comment.

#TODO
1. TODO