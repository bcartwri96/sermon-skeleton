# designated file for helper functions.
import feedgen as fg
import src.conf as cf
import flask as fl
from src.controllers.aws.index import Aws

def get_links(sermon_db, aws):
    # sermon_db is the array of objects we want the links for
    # aws is the object which makes the call. more info at src/ctrls/aws/index
    data = {}

    for sermon in sermon_db:
        # dict the sermon id with the urls required so we can
        # fetch client side
        data[sermon.id] = [aws.get_obj_url(sermon.aws_key_media), \
        aws.get_obj_url(sermon.aws_key_thumb)]
    return data

def produce_feed(sermons, links, connection):
    from feedgen.feed import FeedGenerator
    from datetime import datetime
    import pytz #lib to make datetime objects timezone aware.

    org_name = cf.read_config('MAIN', 'org_name')
    org_email = cf.read_config('MAIN', 'org_email')
    org_link = cf.read_config('MAIN', 'org_link')
    org_logo_link = "https://s3-ap-southeast-2.amazonaws.com/sermon-skeleton/index.png"
    # org_logo_link = fl.url_for('static', filename='img/ico.ico')

    fg = FeedGenerator()
    fg.load_extension('podcast')

    fg.title(org_name+" Podcast")
    fg.author({'name': org_name, 'email': org_email})
    fg.link(href=org_link)
    fg.logo(org_logo_link)
    fg.description(org_name+" sermons. Available for all.")
    fg.language('en')

    fg.podcast.itunes_category('Religion & Spirituality', 'Christianity')
    fg.podcast.itunes_explicit("clean")

    for sermon in sermons:
        fe = fg.add_entry()
        fe.id(links[sermon.id][0])
        fe.title(sermon.title)
        if sermon.description == '':
            fe.description("No description for this sermon.")
        else:
            fe.description(description=sermon.description, isSummary=True)
            print(sermon.description)
        fe.enclosure(links[sermon.id][0], str(sermon.length), 'audio/mpeg')

        # published takes in a datetime object, but we record date (time is
        # irrelevant...) so we need to instantiate a time to supply Feedgen
        date = datetime.combine(sermon.date_given, datetime.min.time())
        timezone = pytz.timezone("Australia/Sydney")
        date_tz = timezone.localize(date)
        fe.published(date_tz)

    fg.rss_file('podcast.xml')
    uploaded = connection.upload_resource('podcast.xml', 'xml', 'podcast.xml')
    if not uploaded:
        print("false for upload")
        old_podcast = connection.get_obj('podcast.xml')
        print("current object: "+ str(old_podcast))
        print("will we delete? "+ str(connection.rm_objs([old_podcast]) ))
        print("Trying again... "+ str(connection.upload_resource('podcast.xml', 'xml', 'podcast.xml')))

    else:
        # initial run case
        pass
