# page designed for the search implementation, to be cleaned up in
# the future!

import src.models.models as ml
import src.scripts.index as scripts
from sqlalchemy import and_, or_

def search_master(query, author, book_bible, series):
    # naive search. check and rank the match as it
    # appears to relate to title.

    if not author and not book_bible and not series:
        res = ml.Sermons.query.filter(ml.Sermons.title.ilike("%"+query+"%")).all()

    elif author and book_bible and series:
        book_bible = ml.Books_Bible.query.get(book_bible)
        author = ml.Authors.query.get(author)
        series = ml.Sermon_Series.query.get(series)
        res = ml.Sermons.query.filter(and_((and_((and_(ml.Sermons.book_bible == book_bible, \
        ml.Sermons.author == author)), ml.Sermons.sermon_series == series)), \
        ml.Sermons.title.ilike("%"+query+"%"))).all()

    elif author and book_bible:
        book_bible = ml.Books_Bible.query.get(book_bible)
        author = ml.Authors.query.get(author)
        res = ml.Sermons.query.filter(and_(ml.Sermons.book_bible ==book_bible, \
        and_(ml.Sermons.title.ilike("%"+query+"%"), \
        ml.Sermons.author == author))).all()

    elif author and series:
        series = ml.Sermon_Series.query.get(series)
        author = ml.Authors.query.get(author)
        res = ml.Sermons.query.filter(and_(ml.Sermons.sermon_series ==series, \
        and_(ml.Sermons.title.ilike("%"+query+"%"), \
        ml.Sermons.author == author))).all()

    elif series and book_bible:
        book_bible = ml.Books_Bible.query.get(book_bible)
        series = ml.Sermon_Series.query.get(series)
        res = ml.Sermons.query.filter(and_(ml.Sermons.book_bible ==book_bible, \
        and_(ml.Sermons.title.ilike("%"+query+"%"), \
        ml.Sermons.sermon_series == series))).all()

    elif author:
        author = ml.Authors.query.get(author)
        res = ml.Sermons.query.filter(ml.Sermons.author == author).all()

    elif series:
        series = ml.Sermon_Series.query.get(series)
        res = ml.Sermons.query.filter(ml.Sermons.sermon_series == series).all()

    elif book_bible:
        b = ml.Books_Bible.query.get(book_bible)
        res = ml.Sermons.query.filter(ml.Sermons.book_bible == b).all()

    else:
        res = []

    return res
