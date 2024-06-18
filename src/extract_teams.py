#!/usr/bin/env python3

import json

with open('matches.json') as matches_file:
    matches = json.load(matches_file)

teams = {}
for match in matches:
    group = match.get('group')
    if group is None:
        continue
    for team in (match['homeTeam'], match['awayTeam']):
        team_code = team['countryCode']
        if team_code in teams:
            continue  # Skip seen teams

        teams[team_code] = {
            'code': team_code,
            'name': team['translations']['countryName']['EN'],
            'group': group['metaData']['groupName'].split()[-1],
            'group_idx': group['teams'].index(team['id'])
        }

teams = sorted(teams.values(), key=lambda t: (t['group'], t['group_idx']))
from pprint import pprint
pprint(teams)
