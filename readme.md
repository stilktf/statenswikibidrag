# Statens wikibidrag

Sporer Wikipedia bidrag fra statlige organisasjoner (det vil si, Stortinget, Miljødirektoratet osv)

## Oppsett

Nettsiden er skrevet med Python, og bruker hovedsaklig bibliotekene [Flask](https://flask.palletsprojects.com) og [peewee](http://docs.peewee-orm.com/en/latest/).

For å sette opp nettsiden, anbefaler jeg deg å bruke en [venv](https://docs.python.org/3/library/venv.html), spesielt for utvikling.

```
python3 -m venv venv/ # Lag en venv
.\venv\Scripts\Activate.ps1 # PowerShell (Windows/Linux/macOS)
venv\Scripts\activate.bat # Batch (Windows, ledetekst (har ikke testest!))
source venv/Scripts/activate # bash/zsh (UNIX og UNIX-like operativsystem som Linux eller macOS)
```

Når du har gjort det, kan du installere pakkene nettsiden bruker:

```
pip install -r requirements.txt
```

Selvfølgelig, når det er gjort, kan du bare kjøre denne kommandoen:

```
flask --app main run --debug
```

eller, så går det kun å kjøre

```
python app.py
```