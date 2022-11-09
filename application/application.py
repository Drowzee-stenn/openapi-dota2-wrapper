from datetime import timedelta

from api_controller.api import API
from core.core import *
from database_controller.database import Database


class DataHelper:
    def __init__(self, match_data, account_id):
        self.match_data = match_data
        for index, current_player in enumerate(match_data['players']):
            if current_player.get('account_id') == account_id:
                self.user_data = current_player
                self.player_position_id = index
        self.teamfight_data = self.match_data['teamfights']

    def prepare_player_data(self):
        self.user_data['hero_name'] = get_heroname_by_id(self.user_data['hero_id'])
        self.user_data['laning_role'] = get_lane_by_role_id(self.user_data['lane_role'])

    def prepare_match_data(self):
        self.match_data['datetime'] = convert_unix_to_datetime(self.match_data['start_time'])

    def prepare_teamfight_data(self):
        teamfight_data = [item['players'][self.player_position_id] for item in self.match_data['teamfights']]
        teamfights_start = [item['start'] for item in self.match_data['teamfights']]
        teamfights_length = [item['end'] - item['start'] for item in self.match_data['teamfights']]

        for index, item in enumerate(teamfight_data):
            item['start'] = teamfights_start[index]
            item['length'] = teamfights_length[index]

        self.teamfight_data = teamfight_data
        player_stats = {'participation': 0}

        for index, teamfight in enumerate(self.teamfight_data, 1):
            if teamfight['damage'] or teamfight['healing'] or teamfight['deaths']:
                player_stats['participation'] += 1
            else:
                self.teamfight_data[index - 1] = None

        player_stats['participation_percent'] = int(player_stats['participation'] / index * 100)
        print(f'Total amount of teamfights: {index}')
        print(f'You participated in {player_stats["participation"]} teamfights. '
              f'Your participation rate is {player_stats["participation_percent"]}%')

        each_fight_impact = [sum((item['damage'], item['healing'])) if item else 0 for item in self.teamfight_data]

        player_stats['total_impact'] = sum(each_fight_impact)
        player_stats['average_impact'] = int(player_stats['total_impact'] / player_stats["participation"])
        print(f'Total impact in this game: {player_stats["total_impact"]}\n'
              f'Average impact in teamfights: {player_stats["average_impact"]}')

        def impact_per_second(item): return item[0] // item[1]
        b = [impact_per_second(item) for item in list(zip(each_fight_impact, teamfights_length))]
        player_stats['best_fight_average_impact'] = max(b)
        best_fight_start = timedelta(seconds=teamfight_data[b.index(player_stats["best_fight_average_impact"])]["start"])
        best_fight_length = teamfight_data[b.index(player_stats["best_fight_average_impact"])]["length"]
        print(f'Your best teamfight happened at {best_fight_start}, '
              f'with average impact of {player_stats["best_fight_average_impact"]} every second for {best_fight_length} seconds')
        pass


class Application:

    def __init__(self, account_id: int = None):
        self.data = None
        self.database = Database()
        self.api = API()

        if isinstance(account_id, int):
            self.account_id = account_id

    def get_info_by_match_id(self, match_id: str):

        print('Match id = ', match_id)

        self.data = DataHelper(self.api.get_match_info(match_id), self.account_id)

        if self.database.check_match_existence(match_id):

            self.data.prepare_player_data()
            self.data.prepare_match_data()
            self.data.prepare_teamfight_data()

            self.database.insert_into_table('parsed_matches_history',
                                            self.data.match_data['match_id'],
                                            self.data.user_data['hero_name'],
                                            self.data.user_data['laning_role']
                                            )

            self.database.insert_into_table('parsed_matches_general_data',
                                            self.data.match_data['match_id'],
                                            self.data.user_data['kills'],
                                            self.data.user_data['deaths'],
                                            self.data.user_data['assists'],
                                            self.data.user_data['last_hits'],
                                            self.data.user_data['denies'],
                                            self.data.user_data['net_worth'],
                                            self.data.user_data['gold_per_min'],
                                            self.data.user_data['xp_per_min'],
                                            self.data.user_data['hero_damage'],
                                            self.data.user_data['tower_damage'],
                                            self.data.user_data['hero_healing']
                                            )
            self.data.prepare_teamfight_data()
            self.database.insert_into_table('parsed_matches_teamfight',
                                            )
        else:
            print('Match has already been parsed')
