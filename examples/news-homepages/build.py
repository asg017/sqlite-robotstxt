import httpx
import sqlite3
import sqlite_xsv
from sys import argv
from urllib.parse import urlparse


db = sqlite3.connect(argv[1])

db.enable_load_extension(True)
sqlite_xsv.load(db)
db.load_extension("../../dist/debug/robotstxt0")
db.enable_load_extension(False)

db.executescript('''
CREATE VIRTUAL TABLE temp.sites_csv USING csv(filename="sites.csv");
CREATE TABLE sites(
  handle text primary key,
  url,
  name,
  location,
  timezone,
  country,
  language,
  bundle,
  wait,
  robotstxt
);

insert into sites
select
  *,
  null as robotstxt
from temp.sites_csv;
''')

BATCH_SIZE = 50

initial = db.execute("select count(*) from sites where robotstxt is null").fetchone()[0]

while True:
  remaining = db.execute("select count(*) from sites where robotstxt is null").fetchone()[0]
  done = initial - remaining
  print(f"[{done}/{initial} {done/initial:.2%}]")

  chunk = db.execute("select rowid, url from sites where robotstxt is null limit ?", [BATCH_SIZE]).fetchall()

  if len(chunk) == 0:
    break

  updates = []

  for row in chunk:
    rowid, url = row
    robotstxt_url = urlparse(url)._replace(path="robots.txt").geturl()
    try:
      response = httpx.get(robotstxt_url, follow_redirects=True)
      robotstxt = response.text
    except Exception:
      robotstxt = ''
    updates.append((robotstxt, rowid))

  db.executemany("update sites set robotstxt = ? where rowid = ?", updates)
  db.commit()

db.executescript("""

CREATE TABLE sites_robotstxt_rules(
  handle text,
  user_agent TEXT,
  source INT,
  rule_type TEXT,
  path TEXT,
  foreign key(handle) references sites(handle)
);
insert into sites_robotstxt_rules
  select
    sites.handle,
    rules.*
  from sites
  join robotstxt_rules(sites.robotstxt) as rules
""")

db.commit()
