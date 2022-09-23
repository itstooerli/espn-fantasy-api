from turtle import position
from dotenv import load_dotenv
load_dotenv()
import requests
import json
import os

class Team:
    def __init__(self, league_member_id=None, credentials='', owner_name='', team_name=''):
        self.league_member_id = league_member_id
        self.credentials = credentials
        self.owner_name = owner_name
        self.team_name = team_name
    
    def __str__(self):
        return f'{self.league_member_id}, {self.credentials}: {self.owner_name}, {self.team_name}'

    def __repr__(self):
        return f'{self.league_member_id}, {self.credentials}: {self.owner_name}, {self.team_name}'

class Player:
    def __init__(self, athlete_id=None, player_name='', position_abbr=''):
        self.athlete_id = athlete_id
        self.player_name = player_name
        self.position_abbr = position_abbr
    
    def __repr__(self):
        return f'{self.player_name}, {self.position_abbr} : {self.athlete_id}'

def find_player_by_id(playerId: str):
    response = requests.get(f'https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/{playerId}')
    response_json = response.json()

    try:
        return Player(playerId, response_json['athlete']['displayName'], response_json['athlete']['position']['abbreviation'])
    except:
        print(playerId, response_json)
        return Player()

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

# with open("offers_report1.json", "w") as outfile:
#     json.dump(response.json(), outfile, indent=2)

# for transaction in response.json()['transactions']:
#     print(transaction)

## Processing Member/Team Information
members = {}

for member in response.json()['members']:
    members[member['id']] = f"{member['firstName']} {member['lastName']}"

teams_by_league_member_id = {}
teams_by_credentials = {}

for team in response.json()['teams']:
    new_team = Team(team['id'], team['primaryOwner'], members[team['primaryOwner']], f"{team['location']} {team['nickname']}")
    teams_by_league_member_id[team['id']] = teams_by_credentials[team['primaryOwner']] = new_team


# print(teams_by_credentials)

## Processing Transactions
players = {}
# print(response.json()['transactions'][0]['items'][0]['fromTeamId'], \
#     find_player_by_id(response.json()['transactions'][0]['items'][0]['playerId']), \
#         response.json()['transactions'][0]['items'][0]['toTeamId'], \
#             response.json()['transactions'][0]['items'][0]['type'])

output_file = open('transactions.txt', 'w')

for transaction in response.json()['transactions']:
    output = ''
    for item in transaction['items']:
        try:
            fromTeamId = teams_by_league_member_id[item['fromTeamId']].owner_name
        except:
            fromTeamId = 'Free Agency'
        
        player = find_player_by_id(item['playerId'])
        player_name = player.player_name
        player_position = player.position_abbr

        try:
            toTeamId = teams_by_league_member_id[item['toTeamId']].owner_name
        except:
            toTeamId = 'Free Agency'

        output += f"{fromTeamId} {item['type']} {player_name},{player_position} {toTeamId}\n"
    # print(output)
    output_file.write(output)
    output_file.write('\n')

output_file.close()

# print(find_player_by_id('3115375'))

# def main():
#     app = MainApplication()
#     app.mainloop()


# if __name__ == "__main__":
#     main()