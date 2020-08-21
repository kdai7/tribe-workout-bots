import os
import urllib.parse
import urllib.request
import psycopg2

from psycopg2 import sql
from slack_api import *

from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

#CREATE TABLE wreck_data(name text, num_posts SMALLINT, num_workouts SMALLINT, num_throws SMALLINT, num_cardio SMALLINT, num_gym SMALLINT, workout_score numeric(4, 1), last_post DATE, slack_id CHAR(9), last_time BIGINT)

def add_num_posts(mention_id, event_time, name, channel_id):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "UPDATE wreck_data SET num_posts=num_posts+1 WHERE slack_id = %s"),
            [mention_id[0]])
        if cursor.rowcount == 0 and channel_id == 'C018V6K1PFH': #"C013LDTN13Q":    #comment: add channel id here
            cursor.execute(sql.SQL("INSERT INTO wreck_data VALUES (%s, 1, 0, 0, 0, 0, 0, now(), %s, %s)"),
                           [name, mention_id[0], event_time])
            send_debug_message("%s is new to Wreck" % name)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)
        return True

def collect_stats(datafield, rev):
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        # get all of the people who's workout scores are greater than -1 (any non players have a workout score of -1)
        cursor.execute(sql.SQL(
            "SELECT * FROM wreck_data WHERE workout_score > -1.0"), )
        leaderboard = cursor.fetchall()
        leaderboard.sort(key=lambda s: s[6], reverse=rev)  # sort the leaderboard by score descending
        string1 = "Leaderboard:\n"
        # for x in range(0, len(leaderboard)):
        #     string1 += '%d) %s with %.1f point(s); %.1d throw(s); %.1d sprint(s); %.1d lift(s). \n' % (x + 1, leaderboard[x][0],
        #         leaderboard[x][6], leaderboard[x][3], leaderboard[x][4], leaderboard[x][5])
        for x in range(0, len(leaderboard)):
            string1 += '%d) %s with %.1f point(s) \n' % (x + 1, leaderboard[x][0], leaderboard[x][6])
        cursor.close()
        conn.close()
        return string1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)

def get_group_info():
    url = "https://slack.com/api/users.list?token=" + os.getenv('BOT_OAUTH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def get_emojis():
    url = 'https://slack.com/api/emoji.list?token=' + os.getenv('OAUTH_ACCESS_TOKEN')
    json = requests.get(url).json()
    return json


def add_to_db(channel_id, names, addition, gym_num, throw_num, cardio_num, num_workouts, ids):  # add "addition" to each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for x in range(0, len(names)):
            print("starting", names[x])
            cursor.execute(sql.SQL(
                "SELECT workout_score FROM wreck_data WHERE slack_id = %s"), [str(ids[x])])
            try:
                score = cursor.fetchall()[0][0]
                score = int(score)
            except:
                #for mentions that haven't posted before
                cursor.execute(sql.SQL("INSERT INTO wreck_data VALUES (%s, 0, 0, 0, 0, 0, 0, now(), %s, %s)"),
                           [names[x], str(ids[x]), '000000000'])
                send_debug_message("%s is new to Wreck" % names[x])
                cursor.execute(sql.SQL(
                "SELECT workout_score FROM wreck_data WHERE slack_id = %s"), [str(ids[x])])
                score = cursor.fetchall()[0][0]
                score = int(score)
            if score != -1 and channel_id == 'C018V6K1PFH': #"C013LDTN13Q":   #comment add channel id here
                cursor.execute(sql.SQL("""
                    UPDATE wreck_data SET num_workouts=num_workouts+%s,
                    num_throws=num_throws+%s, num_cardio=num_cardio+%s, num_gym=num_gym+%s,
                    workout_score=workout_score+%s, last_post=now() WHERE slack_id = %s
                    """),
                    [str(num_workouts), str(throw_num), str(cardio_num), str(gym_num), str(addition), ids[x]])
                conn.commit()
                send_debug_message("committed %s with %s points" % (names[x], str(addition)))
                print("committed %s" % names[x])
                num_committed += 1
            else:
                send_debug_message("invalid workout poster found " + names[x])
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed


def get_req(mention_id):
    cursor = None
    conn = None
    req_string = ""
    try:
        urllib.parse.uses_netloc.append("postgres")
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "SELECT * FROM wreck_data WHERE slack_id = %s"), [mention_id[0]])
        entry = cursor.fetchall()
        req_string += '%s requirements fulfilled: %.1d throws; %.1d cardio; %.1d lifts.' % (entry[x][0], entry[x][3], entry[x][4], entry[x][5])
        cursor.close()
        conn.close()
        return req_string
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(error)


def subtract_from_db(names, subtraction, ids):  # subtract "subtraction" from each of the "names" in the db
    cursor = None
    conn = None
    num_committed = 0
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        for x in range(0, len(names)):
            cursor.execute(sql.SQL(
                "UPDATE wreck_data SET workout_score = workout_score - %s WHERE slack_id = %s"),
                [subtraction, ids[x]])
            conn.commit()
            send_debug_message("subtracted %s" % names[x])
            num_committed += 1
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
        return num_committed


def reset_scores():  # reset the scores of everyone
    cursor = None
    conn = None
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL("""
            UPDATE wreck_data SET num_workouts = 0, num_throws = 0, num_cardio = 0,
            num_gym = 0, workout_score = 0, last_post = now() WHERE workout_score != -1
        """))
        # cursor.execute(sql.SQL(
        #     "DELETE FROM tribe_workouts"
        # ))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()


def reset_talkative():  # reset the num_posts of everyone
    cursor = None
    conn = None
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(sql.SQL(
            "UPDATE wreck_data SET num_posts = 0 WHERE workout_score != -1"))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()

def add_workout(name, slack_id, workout_type):
    cursor = None
    conn = None
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        # cursor = conn.cursor()
        # cursor.execute(sql.SQL("INSERT INTO tribe_workouts VALUES (%s, %s, %s, now())"), [str(name), str(slack_id), str(workout_type)])
        # conn.commit()
        # send_debug_message("Committed " + name + " to the workout list")
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()

def get_workouts_after_date(date, type, slack_id):
    cursor = None
    conn = None
    workouts = []
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        # cursor = conn.cursor()
        # cursor.execute(sql.SQL("SELECT * from tribe_workouts WHERE slack_id=%s and workout_date BETWEEN %s and now() and workout_type=%s"),
        #                [slack_id, date, "!" + type])
        # workouts = cursor.fetchall()
        # conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return workouts

def get_group_workouts_after_date(date, type):
    cursor = None
    conn = None
    workouts = []
    print(date, type)
    try:
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        # cursor = conn.cursor()
        # cursor.execute(sql.SQL("SELECT * from tribe_workouts WHERE workout_date BETWEEN %s and now() and workout_type=%s"),
        #                [date, "!" + type])
        # workouts = cursor.fetchall()
        # conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        send_debug_message(str(error))
    finally:
        if cursor is not None:
            cursor.close()
            conn.close()
    return workouts
