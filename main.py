from dotenv import load_dotenv
load_dotenv()
import requests
import json
import os
from datetime import datetime

POSITION_MAP = {
    0: 'QB',
    1: 'TQB',
    2: 'RB',
    3: 'RB/WR',
    4: 'WR',
    5: 'WR/TE',
    6: 'TE',
    7: 'OP',
    8: 'DT',
    9: 'DE',
    10: 'LB',
    11: 'DL',
    12: 'CB',
    13: 'S',
    14: 'DB',
    15: 'DP',
    16: 'D/ST',
    17: 'K',
    18: 'P',
    19: 'HC',
    20: 'BE',
    21: 'IR',
    22: '',
    23: 'RB/WR/TE',
    24: 'ER',
    25: 'Rookie',
    'QB': 0,
    'RB': 2,
    'WR': 4,
    'TE': 6,
    'D/ST': 16,
    'K': 17,
    'FLEX': 23,
    'DT': 8,
    'DE': 9,
    'LB': 10,
    'DL': 11,
    'CB': 12,
    'S': 13,
    'DB': 14,
    'DP': 15,
    'HC': 19
}

class Team:
    def __init__(self, league_member_id=None, credentials='', owner_name='', team_name=''):
        self.league_member_id = league_member_id
        self.credentials = credentials
        self.owner_name = owner_name
        self.team_name = team_name

    def __repr__(self):
        return f'{self.league_member_id}, {self.credentials}: {self.owner_name}, {self.team_name}'

class Player:
    def __init__(self, athlete_id=None, player_name='', position_abbr=''):
        self.athlete_id = athlete_id
        self.player_name = player_name
        self.position_abbr = position_abbr
    
    def __repr__(self):
        return f'{self.player_name}, {self.position_abbr} : {self.athlete_id}'

class MainApplication:
    def __init__(self):
        self.player_base = {}

        try:
            self.league_id = os.environ.get('LEAGUE_ID')
        except:
            self.league_id = input('Enter your ESPN league id: ')

        try:
            self.cookie_swid = os.environ.get('SWID')
        except:
            self.cookie_swid = input('Enter SWID cookie: ')

        try:
            self.cookie_espn_s2 = os.environ.get('ESPN_S2')
        except:
            self.cookie_espn_s2 = input('Enter ESPN_S2 cookie: ')
        
        self.get_player_base()
    
    def get_player_base(self):
        ## Refining player base
        endpoint = 'https://fantasy.espn.com/apis/v3/games/' + 'ffl' + '/seasons/' + '2022' + '/players'
        params = {'view': 'players_wl'}
        filters = {'filterActive': {'value': True}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        cookies = {"swid":      self.cookie_swid,
                "espn_s2":   self.cookie_espn_s2}

        response = requests.get(endpoint, params=params, headers=headers, cookies=cookies)
        print(response.url)

        for player in response.json():
            player_id = player['id']
            player_full_name = player['fullName']
            player_position = POSITION_MAP[player['defaultPositionId']]
            
            self.player_base[player_id] = (player_full_name, player_position)
        
            if player_full_name not in self.player_base:
                self.player_base[player_full_name] = (player_id, player_position)

    # def find_player_by_id(self, playerId: str):
    #     if playerId in self.players:
    #         return self.players[playerId]

    #     response = requests.get(f'https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/{playerId}')
    #     response_json = response.json()
        
    #     if response.status_code != 200:
    #         print(playerId, response_json)
    #         return Player()
        
    #     self.players[playerId] = Player(playerId, response_json['athlete']['displayName'], response_json['athlete']['position']['abbreviation'])
    #     return self.players[playerId]
    
    def write_offers_reports(self, output_file, years: list[int], scoring_periods: list[int]):
        # year = 2021
        ## Offers Reports
        for year in years:
            output_file.write(f'{year}\n')

            url = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{self.league_id}'
            cookies = {"swid":      self.cookie_swid,
                       "espn_s2":   self.cookie_espn_s2}
            
            for scoring_period in scoring_periods:
                params = {"scoringPeriodId": scoring_period, 
                        "view": ["mDraftDetail", "mStatus", "mSettings", "mTeam", "mTransactions2", "modular", "mNav"]}
                # filters = {"topics": {"limit": 50}}
                # headers = {"x-fantasy-filter": json.dumps(filters)}
                
                response = requests.get(url, params=params, cookies=cookies)
                if response.status_code != 200:
                    # output_file.write(response.json)
                    print(response.json)
                    continue
                else:
                    print(response.url)
                    with open("offers_report.json", "w") as outfile:
                        json.dump(response.json(), outfile, indent=2)

                ## Processing Member/Team Information
                members = {}

                for member in response.json()['members']:
                    members[member['id']] = f"{member['firstName']} {member['lastName']}"

                teams_by_league_member_id = {}
                teams_by_credentials = {}

                for team in response.json()['teams']:
                    new_team = Team(team['id'], team['primaryOwner'], members[team['primaryOwner']], f"{team['location']} {team['nickname']}")
                    teams_by_league_member_id[team['id']] = teams_by_credentials[team['primaryOwner']] = new_team
                
                ## Processing Transactions
                if 'transactions' not in response.json():
                    continue

                for transaction in response.json()['transactions']:
                    header = f"Type: {transaction['executionType']} - {transaction['type']}, Bid Amount: {transaction['bidAmount']}, Date: {datetime.fromtimestamp(transaction['proposedDate'] / 1000)}\n"
                    if 'status' in transaction:
                        header += f"Status: {transaction['status']},"
                    if 'teamId' in transaction:
                        header += f"Team: {teams_by_league_member_id[transaction['teamId']].owner_name}"
                    
                    output = '\n'

                    if 'items' in transaction:
                        for item in transaction['items']:
                            if item['type'] in ("LINEUP", "DRAFT"):
                                continue

                            try:
                                fromTeamId = teams_by_league_member_id[item['fromTeamId']].owner_name
                            except:
                                fromTeamId = 'Free Agency'
                            
                            try: 
                                player_name, player_position = self.player_base[item['playerId']]
                            except:
                                player_response = requests.get(f"https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/{item['playerId']}")
                                response_json = player_response.json()
                                if player_response.status_code != 200:
                                    player_name = player_position = ''
                                else:
                                    player_name = response_json['athlete']['displayName']
                                    player_position = response_json['athlete']['position']['abbreviation']

                            try:
                                toTeamId = teams_by_league_member_id[item['toTeamId']].owner_name
                            except:
                                toTeamId = 'Free Agency'

                            if item['type'] == "ADD":
                                output += f"{toTeamId} {item['type']} {player_name},{player_position} from {fromTeamId}\n"
                            else:
                                output += f"{fromTeamId} {item['type']} {player_name},{player_position} to {toTeamId}\n"
                            
                    output = header + output
                    # print(output)
                    output_file.write(output)
                    output_file.write('\n')

def main():
    app = MainApplication()
    years = [2019, 2020, 2021, 2022]

    for year in years:
        output_file = open(f'transactions-iv-{year}.txt', 'w')
        # years = [2018] ## DOES NOT WORK FOR OLDER THAN 2018
        # years = [2019]
        # years = [2020]
        # years = [2021]
        scoring_periods = list(range(0,18)) ## Previous years

        # years = [2022]
        # scoring_periods = list(range(0, 3))
        app.write_offers_reports(output_file, [year], scoring_periods)
        output_file.close()

if __name__ == "__main__":
    main()

