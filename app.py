import requests
from flask import Flask, render_template
from peewee import *
from datetime import datetime
import time
import atexit
from urllib.parse import quote
from flask_caching import Cache
from flask_apscheduler import APScheduler
import threading

argh = []

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "SCHEDULER_API_ENABLED": False
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
db = SqliteDatabase("database/db.db")

scheduler = APScheduler()
scheduler.init_app(app)

class Bidrag(Model):
    link = CharField(unique=True)
    ip = CharField()
    iprange = CharField()
    date = IntegerField()
    title = CharField()
    comment = CharField()
    size = IntegerField()
    wiki = CharField()
    body = CharField()
    revid = IntegerField()

    class Meta:
        database = db

db.connect()
db.create_tables([Bidrag])

def check():
    app.logger.info("Getting Wikipedia contributions")
    # Reset argh
    argh.clear()
    wikis = ["en", "no"]
    # Stortinget - Kripos - Miljødirektoratet - MET Oslo - Norsk Institutt for Vannforskning (NIVA) - NRK - NRK - Norsk Hydro - Norsk Hydro - Politiets IKT-tjenester
    ranges = ["85.88.64.0/19", "45.88.116.0/22", "185.76.84.0/22", "157.249.0.0/16", "151.157.0.0/16", "160.68.0.0/16", "185.97.188.0/22", "149.209.0.0/16", "149.209.0.0/16", "163.174.0.0/18"]

    body = ""

    for wiki in wikis:
        app.logger.info(f"Getting {wiki} Wikipedia contributions")
        for current_range in ranges:
            app.logger.info(f"Getting contributions for IP range {current_range}")
            # This is probably a little fucked up, TODO: make this less fucked up maybe
            if current_range == "85.88.64.0/19":
                body = "Stortinget"
            elif current_range == "45.88.116.0/22":
                body = "Kripos"
            elif current_range == "185.76.84.0/22":
                body = "Miljødirektoratet"
            elif current_range == "157.249.0.0/16":
                body = "MET Oslo"
            elif current_range == "151.157.0.0/16":
                body = "NIVA"
            elif current_range == "160.68.0.0/16" or current_range == "185.97.188.0/22":
                body = "NRK"
            elif current_range == "185.97.188.0/22" or current_range == "149.209.0.0/16":
                body = "Norsk Hydro"
            else:
                body = "Politiets IKT-tjenester"

            r = requests.get(url=f"https://{wiki}.wikipedia.org/w/api.php", params={
                "action": "query",
                "format": "json",
                "list": "usercontribs",
                "uciprange": f"{current_range}",
                "uclimit": "500"
            })

            data = r.json()

            contributions = data["query"]["usercontribs"]

            for contribution in contributions:
                check_contrib = Bidrag.select().where(Bidrag.revid == contribution['revid'])
                if check_contrib:
                    continue
                contribution_db = Bidrag(
                    link=quote(f'https://{wiki}.wikipedia.org/w/index.php/?title={contribution["title"]}&diff=prev&oldid={contribution["revid"]}', safe=":/?=&"),
                    ip=contribution['user'],
                    iprange=current_range,
                    date=iso8601_to_unix_time(contribution['timestamp']),
                    title=contribution['title'],
                    comment=contribution['comment'],
                    size=contribution['size'],
                    wiki=wiki,
                    body=body,
                    revid=contribution['revid']
                    )
                contribution_db.save()

    for contrib in Bidrag.select().order_by(Bidrag.date.desc()):
        bidrag = {
            'link': contrib.link,
            'ip': contrib.ip,
            'iprange': contrib.iprange,
            'date': time.ctime(contrib.date),
            'org_date': contrib.date,
            'title': contrib.title,
            'comment': contrib.comment,
            'size': contrib.size,
            'wiki': contrib.wiki,
            'body': contrib.body,
            'revid': contrib.revid,
        }

        argh.append(bidrag)

def iso8601_to_unix_time(iso8601_string):
    # Assuming iso8601_string is in the format 'YYYY-MM-DDTHH:MM:SSZ'
    utc_datetime = datetime.strptime(iso8601_string, '%Y-%m-%dT%H:%M:%SZ')

    # Convert UTC datetime to Unix time
    unix_time = int(utc_datetime.timestamp())

    return unix_time

@scheduler.task('interval', id="get_contributions", seconds=300, misfire_grace_time=900)
def get_contributions():
    thread = threading.Thread(target=check)
    thread.start()

# Routes

@app.route("/")
@cache.cached(timeout=300)
def index():
    return render_template("index.html", stuff=argh, count=len(argh))

@app.route("/json")
@cache.cached(timeout=300)
def json():
    json = {"count": len(argh), "contributions": argh}
    return json

@app.route("/healthcheck")
def healthcheck():
    return "OK"

def on_exit():
    db.close()

atexit.register(on_exit)

scheduler.start()

scheduler.run_job("get_contributions")

if __name__ == '__main__':
    app.run(debug=True)