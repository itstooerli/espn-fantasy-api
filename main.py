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

class MainApplication:
    def __init__(self):
        self.players = {}

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

    def find_player_by_id(self, playerId: str):
        if playerId in self.players:
            return self.players[playerId]

        response = requests.get(f'https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/{playerId}')
        response_json = response.json()
        
        if response.status_code != 200:
            print(playerId, response_json)
            return Player()
        
        self.players[playerId] = Player(playerId, response_json['athlete']['displayName'], response_json['athlete']['position']['abbreviation'])
        return self.players[playerId]
    
    def write_offers_reports(self, output_file, years: list[int], scoring_period_ids: list[int] = list(range(0,19))):
        # year = 2021
        # scoring_period_id = 17
        ## Offers Reports
        for year in years:
            output_file.write(f'{year}\n')

            url = f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{self.league_id}'
            cookies = {"swid":      self.cookie_swid,
                       "espn_s2":   self.cookie_espn_s2}

            for scoring_period_id in scoring_period_ids:
                output_file.write(f'Scoring Period: {scoring_period_id}\n')
                
                params = {"scoringPeriodId": scoring_period_id,
                        "view": ["mDraftDetail", "mStatus", "mSettings", "mTeam", "mTransactions2", "modular", "mNav"]}

                response = requests.get(url, params=params, cookies=cookies)
                if response.status_code != 200:
                    output_file.write(response.json)
                    # print(response.json)
                    continue
                else:
                    print(response.url)

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
                    if not transaction or transaction['executionType'] == "CANCEL":
                        continue

                    header = f"Type: {transaction['executionType']}, Bid Amount: {transaction['bidAmount']}\n"
                    output = ''

                    if 'items' not in transaction:
                        print(transaction)
                        continue

                    for item in transaction['items']:
                        if item['type'] in ("LINEUP", "DRAFT"):
                            continue

                        try:
                            fromTeamId = teams_by_league_member_id[item['fromTeamId']].owner_name
                        except:
                            fromTeamId = 'Free Agency'
                        
                        player = self.find_player_by_id(item['playerId'])
                        player_name = player.player_name
                        player_position = player.position_abbr

                        try:
                            toTeamId = teams_by_league_member_id[item['toTeamId']].owner_name
                        except:
                            toTeamId = 'Free Agency'

                        if item['type'] == "ADD":
                            output += f"{toTeamId} {item['type']} {player_name},{player_position} from {fromTeamId}\n"
                        else:
                            output += f"{fromTeamId} {item['type']} {player_name},{player_position} to {toTeamId}\n"
                        
                    if output:
                        output = header + output
                        # print(output)
                        output_file.write(output)
                        output_file.write('\n')

def main():
    app = MainApplication()
    output_file = open('transactions2021.txt', 'w')
    years = [2021]
    app.write_offers_reports(output_file, years)
    output_file.close()

if __name__ == "__main__":
    main()

    ## Refining player base
    # endpoint = 'https://fantasy.espn.com/apis/v3/games/' + 'ffl' + '/seasons/' + '2022' + '/players'
    # params = {'view': 'players_wl'}
    # filters = {'filterActive': {'value': True}}
    # headers = {'x-fantasy-filter': json.dumps(filters)}

    # league_id = os.environ.get('LEAGUE_ID')
    # cookie_swid = os.environ.get('SWID')
    # cookie_espn_s2 = os.environ.get('ESPN_S2')
    # cookies = {"swid":      cookie_swid,
    #         "espn_s2":   cookie_espn_s2}

    # response = requests.get(endpoint, params=params, headers=headers, cookies=cookies)
    # print(response.status_code, response.url)
    # print(len(response.json()))

    # player_map = {}

    # for player in response.json():
    #     player_map[player['id']] = player['fullName']
    
    #     if player['fullName'] not in player_map:
    #         player_map[player['fullName']] = player['id']
    

    # print(player_map[3115375])
    # print(player_map['Darrel Williams'])
    # print(player_map[-16034])
    

