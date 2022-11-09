import os
import json
from datetime import datetime


def get_heroname_by_id(hero_id):
    with open(os.getcwd() + '\\resources\\dictionaries\\heroes.json') as file:
        heroes = json.loads(file.read())
        for hero in heroes:
            if hero['id'] == hero_id:
                return hero['localized_name']
        raise Exception(f'hero with id {hero_id} was not found')


def convert_unix_to_datetime(unix_time):
    date = datetime.fromtimestamp(unix_time)
    return f'{date.year}-{date.month}-{date.day}'


def get_lane_by_role_id(role_id):
    with open(os.getcwd() + '\\resources\\dictionaries\\roles.json') as file:
        roles = json.loads(file.read())
        for role in roles:
            if role['id'] == role_id:
                return role['role']
        raise Exception(f'hero with id {role_id} was not found')
