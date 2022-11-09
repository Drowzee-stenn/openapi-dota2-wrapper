from datetime import timedelta

from core.api.api import API
from core import core
from core.database.database import Database
from logger.log import logger


class DataHelper:

    def __init__(self, match_data, account_id):
        self.player_stats = None
        self.match_data = match_data
        self.teamfight_data = self.match_data['teamfights']

        for index, current_player in enumerate(match_data['players']):
            if current_player.get('account_id') == account_id:
                self.user_data = current_player
                self.user_data['player_position_id'] = index  # player position in data [0:9]
                return
        logger.debug(f'Player {account_id} was not found in match id {self.match_data["match_id"]}')

    def prepare_player_data(self):
        self.user_data['hero_name'] = core.get_heroname_by_id(self.user_data['hero_id'])
        self.user_data['laning_role'] = core.get_lane_by_role_id(self.user_data['lane_role'])

    def prepare_match_data(self):
        self.match_data['datetime'] = core.convert_unix_to_datetime(self.match_data['start_time'])

    def prepare_teamfight_data(self):
        player_data = [item['players'][self.user_data['player_position_id']] for item in self.match_data['teamfights']]
        self.player_stats: dict = {'participation': 0}

        if player_data:
            self.teamfight_data = player_data
        else:
            logger.debug(f'Teamfight data was not found for match id {self.match_data["match_id"]}')
            return

        # Add the info about start/end of a teamfight in player_data
        for index, item in enumerate(self.teamfight_data):
            item['time_start'] = self.match_data['teamfights'][index]['start']
            item['time_end'] = self.match_data['teamfights'][index]['end']
            item['time_delta'] = item['time_end'] - item['time_start']

        for index, teamfight in enumerate(self.teamfight_data):
            if teamfight['damage'] or teamfight['healing'] or teamfight['deaths']:
                self.player_stats['participation'] += 1

        self.player_stats['participation_percent'] = int(
            self.player_stats['participation'] / len(self.teamfight_data) * 100)
        print(f'Total amount of teamfights: {len(self.teamfight_data) + 1}')
        print(f'You participated in {self.player_stats["participation"]} teamfights. '
              f'Your participation rate is {self.player_stats["participation_percent"]}%')

        self.player_stats['each_fight_impact'] = [item['damage'] + item['healing'] for item in self.teamfight_data]

        self.player_stats['total_impact'] = sum(self.player_stats['each_fight_impact'])
        self.player_stats['average_impact'] = self.player_stats['total_impact'] // self.player_stats["participation"]
        print(f'Total impact in this game: {self.player_stats["total_impact"]}\n'
              f'Average impact in teamfights: {self.player_stats["average_impact"]}')

        teamfights_length = [fight['time_delta'] for fight in self.teamfight_data]
        b = [impact // time for impact, time in zip(self.player_stats['each_fight_impact'], teamfights_length)]
        self.player_stats['best_fight_average_impact'] = max(b)
        self.player_stats['best_fight_start'] = timedelta(
            seconds=self.teamfight_data[b.index(self.player_stats["best_fight_average_impact"])].get("time_start"))
        print(f'Your best teamfight happened at {self.player_stats["best_fight_start"]}, '
              f'with total impact of {max(self.player_stats["each_fight_impact"])}')


class Application:

    def __init__(self, account_id: int = None):
        self.data = None
        self.database = Database()
        self.api = API()

        if isinstance(account_id, int):
            self.account_id = account_id
        else:
            logger.debug('Account id must be integer-type')

    def get_info_by_match_id(self, match_id: str):

        # if self.database.check_match_existence(match_id):
        #     return

        print('Match id = ', match_id)

        self.data = DataHelper(self.api.get_match_info(match_id), self.account_id)

        self.data.prepare_player_data()
        self.data.prepare_match_data()
        self.data.prepare_teamfight_data()

        self.database.insert_into_table('parsed_matches_history',
                                        self.data.match_data['match_id'],
                                        self.data.user_data['hero_name'],
                                        self.data.user_data['laning_role']
                                        )

        # TODO: target abilities + skill-shots
        return
