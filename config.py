#!/usr/bin/env python

class Config(object):
    FEEDS = (
      { "url" : "http://feeds.bbci.co.uk/news/technology/rss.xml?edition=us", "icon" : "bbc-28.png" },
      { "url" : "https://hackaday.com/blog/feed/", "icon" : "hackaday-28.png" },
      { "url" : "http://www.nova-labs.org/blog/feed/", "icon" : "novalabs-28.png" },
      { "url" : "http://makezine.com/feed/", "icon" : "makezine-28.png" }
    )

class DevelopmentConfig(Config):
    DEBUG = True
