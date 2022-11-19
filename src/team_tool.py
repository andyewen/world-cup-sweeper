import re
import json
import string

split_re = re.compile(r'\s+\|\s+')

fifa_to_iso = {}
group = 'A'

with open('teams.txt') as f:
    for l in f:
        l = l.strip()
        if not l:
            group = chr(ord(group) + 1)
            continue
        name, fifa, iso = split_re.split(l)

        fifa = fifa.upper()
        iso = iso.lower()

        fifa_to_iso[fifa] = iso
        print(f"new Team('{fifa}', '{name}', '{group}'),")


# print(json.dumps(fifa_to_iso, indent=4))
