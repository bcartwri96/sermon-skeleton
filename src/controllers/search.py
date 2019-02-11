from elasticsearch import Elasticsearch

POSTGRES_URL = scripts.get_env_variable("POSTGRES_URL")
POSTGRES_USER = scripts.get_env_variable("POSTGRES_USER")
POSTGRES_PW = scripts.get_env_variable("POSTGRES_PW")
POSTGRES_DB = scripts.get_env_variable("POSTGRES_DB")
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)


search = Elasticsearch(DB_URL)
