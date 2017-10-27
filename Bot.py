import os
import sys
import json
import ast
import urllib.request
import urllib.parse
import psycopg2
from psycopg2 import sql

from urllib.parse import urlencode
from urllib.request import Request, urlopen
urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse("postgres://elyhxqornsxcrs:be4a23f0b58aa36c51146d4582135b3e52137a6453f15f6d27c2380351ef8379@ec2-107-20-193-89.compute-1.amazonaws.com:5432/d69osjej45evcr")

#def like_workout_photo(conversation_id, message_id):
#    url = 'https://api.groupme.com/v3/bots/post/messages'
#    data = {
#        'conversation_id' : conversation_id,
#        'message_id' : message_id
#    }
#    request = Request(url, urlencode(data).encode())
#    json = urlopen(request"/like").read().decode()

def add_workout_to_database():
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cursor = conn.cursor()
    cursor.execute(
        sql.SQL("UPDATE tribe_data SET num_posts = num_posts-6 WHERE {} = %s")
                   .format(sql.Identifier('name')), ['William Syre'])
    cursor.execute("SELECT * FROM tribe_data")
    records = cursor.fetchall()
    print(records)
    cursor.close()

add_workout_to_database()