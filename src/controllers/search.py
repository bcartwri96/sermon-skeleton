# page designed for the search implementation, to be cleaned up in
# the future!

import src.models.models as ml
import src.scripts.index as scripts

POSTGRES_URL = scripts.get_env_variable("POSTGRES_URL")
POSTGRES_USER = scripts.get_env_variable("POSTGRES_USER")
POSTGRES_PW = scripts.get_env_variable("POSTGRES_PW")
POSTGRES_DB = scripts.get_env_variable("POSTGRES_DB")
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

def search_master(query, author, title, book_bible, series):
    # naive search. check and rank the match as it
    # appears to relate to title.

    if title:
        res = ml.Sermons.query.filter(ml.Sermons.title.like("%"+query+"%")).all()

        if res:
            return res
        else:
            return []

    elif title and author:
        res = ml.Sermons.query.filter(_or(ml.Sermons.title.ilike("%"+query+"%"), \
        ml.Sermons.author.ilike("%"+query+"%"))).all()
    else:
        return []
