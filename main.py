from dotenv import load_dotenv
load_dotenv()
import requests
import json
import os

try:
    league_id = os.environ.get('LEAGUE_ID')
except:
    league_id = input('Enter your ESPN league id: ')

try:
    cookie_swid = os.environ.get('SWID')
except:
    cookie_swid = input('Enter SWID cookie: ')

try:
    cookie_espn_s2 = os.environ.get('ESPN_S2')
except:
    cookie_espn_s2 = input('Enter ESPN_S2 cookie: ')

year = 2021
scoring_period_id = 17

## Offers Reports
url = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}'
params = {"scoringPeriodId": scoring_period_id,
          "view": ["mDraftDetail", "mStatus", "mSettings", "mTeam", "mTransactions2", "modular", "mNav"]}
cookies = {"swid": cookie_swid,
           "espn_s2": cookie_espn_s2}

response = requests.get(url, params=params, cookies=cookies)
print(response.url)

with open("offers_report1.json", "w") as outfile:
    json.dump(response.json(), outfile, indent=2)
