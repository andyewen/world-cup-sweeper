<template>
    <div class="container">
        <h1>World Cup 2022 Sweepstake</h1>

        <h2 class="match-header">Matches</h2>
        <div class="match-day-selector">
            <button @click="select_previous_date" :disabled="!can_select_previous_date">
                &lt;
            </button>
            <div class="date" :class="{'is-today': selected_date == today}">
                <div class="month">{{ format_month(selected_date) }}</div>
                <div class="day">{{ format_day(selected_date) }}</div>
            </div>
            <button @click="select_next_date" :disabled="!can_select_next_date">
                &gt;
            </button>
        </div>
        <div class="matches-container">
            <template v-if="matches_grouped_by_date && matches_grouped_by_date[selected_date]">
                <Match v-for="match in matches_grouped_by_date[selected_date]" :key="match.fifa_id"
                    :match="match"
                    :teams_by_code="teams_by_code"
                    :team_code_to_person="team_code_to_person" />
            </template>
            <template v-else-if="!matches_grouped_by_date">
                loading...
            </template>
            <template v-else>
                there are no matches on the selected day!
            </template>
        </div>

        <h2>Players</h2>
        <table class="player-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Teams</th>
                    <th class="hide-small">Wins</th>
                    <th class="hide-small">Teams Left</th>
                    <th v-if="tournament_complete">Prize</th>
                </tr>
            </thead>
            <tbody>
                <tr 
                    v-for="person in people_with_teams_and_stats" 
                    :class="[
                        {
                            'person-row-knocked-out': person.competing_team_count < 1
                        },
                        tournament_complete ? 'final-place-' + person.final_place : '',
                    ]"
                    :key="person.name"
                >
                    <td class="person-name">{{ person.name }}</td>
                    <td>
                        <TeamBadge v-for="team in person.teams" :key="team.code"
                            :team="team" :show_person="false" :knocked_out="team_knocked_out[team.code]"
                            class="team-spaced"
                        />
                    </td>
                    <td class="hide-small">{{ loaded_matches ? person.total_tournament_wins : '?' }}</td>
                    <td class="hide-small">{{ loaded_matches ? person.competing_team_count : '?' }}</td>
                    <td v-if="tournament_complete" class="prize">
                        <template v-if="loaded_matches">
                            <template v-if="person.prize">
                                £{{ person.prize }}
                            </template>
                            <template v-else>
                                —
                            </template>
                        </template>
                        <template v-else>
                            ?
                        </template>
                    </td>
                </tr>
            </tbody>
        </table>
        <div v-if="unallocated_teams.length" class="unallocated-teams">
            <TeamBadge v-for="team in unallocated_teams" :key="team.code"
                :team="team" :show_person="false" :knocked_out="team_knocked_out[team.code]"
                class="team-spaced"
            />
        </div>

        <h2 class="groups-header">Groups</h2>
        <GroupTable v-for="group in groups" :key="group.code"
                    :group="group" :teams_by_code="teams_by_code" :team_code_to_person="team_code_to_person"
                    :team_knocked_out="team_knocked_out" :loaded_matches="loaded_matches"/>

        <p><strong>Good luck!</strong> 🤑</p>
    </div>
</template>

<script>
import GroupTable from './components/GroupTable.vue';
import Match from './components/Match.vue';
import TeamBadge from './components/TeamBadge.vue';

import {dateString, pad2, product} from './utils.js';

import matches from './assets/matches.json';

function Person(name, teams) {
    this.name = name;
    this.teams = teams;
}

function TeamStats() {
    this.goals_scored = 0;
    this.goals_conceded = 0;
    this.wins = 0;
    this.draws = 0;
    this.losses = 0;
}

TeamStats.prototype = {
    get_points: function() {
        return (this.wins * 3) + (this.draws);
    },
    get_played: function() {
        return this.wins + this.draws + this.losses;
    },
    get_goal_difference: function() {
        return this.goals_scored - this.goals_conceded;
    }
}

function Team(code, name, group, knocked_out) {
    this.code = code;
    this.name = name;
    this.group = group;
    this.knocked_out = knocked_out;
    this.flag_url = "flags/" + this.code.toLowerCase() + ".gif";

    this.group_stats = new TeamStats();
    this.tournament_stats = new TeamStats();
}

export default {
    components: {
        GroupTable,
        Match,
        TeamBadge,
    },
    data: function() {
        var teams = [
            new Team('QAT', 'Qatar', 'A'),
            new Team('ECU', 'Ecuador', 'A'),
            new Team('SEN', 'Senegal', 'A'),
            new Team('NED', 'Netherlands', 'A'),

            new Team('ENG', 'England', 'B'),
            new Team('IRN', 'Iran', 'B'),
            new Team('USA', 'USA', 'B'),
            new Team('WAL', 'Wales', 'B'),

            new Team('ARG', 'Argentina', 'C'),
            new Team('KSA', 'Saudi Arabia', 'C'),
            new Team('MEX', 'Mexico', 'C'),
            new Team('POL', 'Poland', 'C'),

            new Team('FRA', 'France', 'D'),
            new Team('AUS', 'Australia', 'D'),
            new Team('DEN', 'Denmark', 'D'),
            new Team('TUN', 'Tunisia', 'D'),

            new Team('ESP', 'Spain', 'E'),
            new Team('CRC', 'Costa Rica', 'E'),
            new Team('GER', 'Germany', 'E'),
            new Team('JPN', 'Japan', 'E'),

            new Team('BEL', 'Belgium', 'F'),
            new Team('CAN', 'Canada', 'F'),
            new Team('MAR', 'Morocco', 'F'),
            new Team('CRO', 'Croatia', 'F'),

            new Team('BRA', 'Brazil', 'G'),
            new Team('SRB', 'Serbia', 'G'),
            new Team('SUI', 'Switzerland', 'G'),
            new Team('CMR', 'Cameroon', 'G'),

            new Team('POR', 'Portugal', 'H'),
            new Team('GHA', 'Ghana', 'H'),
            new Team('URU', 'Uruguay', 'H'),
            new Team('KOR', 'South Korea', 'H'),
        ];

        var people = [
            new Person('Andrew C.',     ['SEN', 'CRC']),
            new Person('Andrew E.',     ['CRO', 'POL']),
            new Person('Anna S.',       ['BRA', 'ECU']),
            new Person('Callum E.',     ['GER', 'TUN']),
            new Person('David H.',      ['USA', 'JPN']),
            new Person('Ewan P.',       ['DEN', 'CMR']),
            new Person('Greig K.',      ['FRA', 'SRB']),
            new Person('John M.',       ['POR', 'QAT']),
            new Person('Michael C.',    ['ESP', 'AUS']),
            new Person('Patrick G.',    ['BEL', 'MAR']),
            new Person('Peder R.',      ['NED', 'KOR']),
            new Person('Ross B.',       ['URU', 'GHA']),
            new Person('Ryan S.',       ['ARG', 'WAL']),
            new Person('Sam W.',        ['MEX', 'CAN']),
            new Person('Scott B.',      ['SUI', 'IRN']),
            new Person('Thomas H.',     ['ENG', 'KSA']),
        ];

        var today = dateString(new Date());

        return {
            teams: teams,
            people: people,
            group_match_pivot: null,  // new Date('2018-06-28T22:00Z'),
            matches: null,
            today: today,
            selected_date: today
        }
    },
    created: function() {
        this.fetch_matches();
        // var self = this,
        //     req = new XMLHttpRequest();
        // req.addEventListener("load", function(e) {
        //     self.load_matches(JSON.parse(this.responseText));
        // });
        // req.open("GET", "matches.json");
        // req.send();
    },
    methods: {
        async fetch_matches() {
            // const response = await fetch('https://worldcupjson.net/matches');
            // const matches = await response.json();
            this.load_matches(matches);
        },
        load_matches: function(matches) {
            var self = this;
            self.matches = matches.sort(function(a, b) {
                if (!a.datetime && !b.datetime) return 0;
                if (!a.datetime) return 1;
                if (!b.datetime) return -1;

                var a = new Date(a.datetime),
                    b = new Date(b.datetime);
                if (a < b) return -1;
                if (a > b) return 1;
                return 0;
            });

            // Clamp selected date inside tournament date range.
            if (self.matches.length) {
                var first_date = self.matches[0].datetime;
                var last_date = self.matches[self.matches.length - 1].datetime;
                if (first_date) {
                    first_date = dateString(first_date);
                    if (self.selected_date < first_date) { 
                        self.selected_date = first_date; 
                    }
                }
                if (last_date) {
                    last_date = dateString(last_date);
                    if (self.selected_date > last_date) { 
                        self.selected_date = last_date; 
                    }
                }
            }

            var completed_matches = this.matches.filter(function(m) {
                return m.status == 'completed';
            });

            completed_matches.forEach(function(match) {
                var home_team = self.teams_by_code[match.home_team.country],
                    away_team = self.teams_by_code[match.away_team.country];
                if (!home_team || !away_team) { return; }

                var add_to_stats = ['tournament_stats'];
                if (match.stage_name === 'First stage') {
                    // Track match in group stats if it is during the group stages.
                    add_to_stats.push('group_stats');
                }

                add_to_stats.forEach(function(stats_key) {
                    var home_stats = home_team[stats_key];
                    var away_stats = away_team[stats_key];

                    if (match.winner_code == home_team.code) {
                        home_stats.wins++;
                        away_stats.losses++;
                    } else if (match.winner_code == away_team.code) {
                        home_stats.losses++;
                        away_stats.wins++;
                    } else {
                        home_stats.draws++;
                        away_stats.draws++;
                    }

                    home_stats.goals_scored += match.home_team.goals;
                    away_stats.goals_scored += match.away_team.goals;

                    home_stats.goals_conceded += match.away_team.goals;
                    away_stats.goals_conceded += match.home_team.goals;
                });
            });
        },
        format_day: function(d) {
            return pad2(new Date(d).getDate());
        },
        format_month: function(d) {
            return [
                'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'
            ][new Date(d).getMonth()]
        },
        select_next_date: function() {
            if (this.can_select_next_date) this.selected_date = this.next_date;
        },
        select_previous_date: function() {
            if (this.can_select_previous_date) this.selected_date = this.previous_date;
        }
    },
    computed: {
        tournament_complete: function() {
            if (!this.matches) return null;

            for (var i = 0; i < this.matches.length; i++) {
                if (this.matches[i].status != 'completed') {
                    return false;
                }
            }
            return true;
        },
        top_three_teams: function() {
            if (!this.matches) return null;

            var final_match = this.matches[this.matches.length - 1];
            var third_place_match = this.matches[this.matches.length - 2];

            return [
                final_match.winner_code,
                final_match.home_team.country == final_match.winner_code ? final_match.away_team.country : final_match.home_team.country,
                third_place_match.winner_code
            ];
        },
        people_with_teams_and_stats: function() {
            var self = this;

            var people = self.people.map(function(person) {
                var teams = person.teams.map(function(team_code) {
                    return self.teams_by_code[team_code];
                }).sort(function(a, b) {
                    var a_knocked_out = self.team_knocked_out[a.code],
                        b_knocked_out = self.team_knocked_out[b.code];
                    if (a_knocked_out == b_knocked_out) return 0;
                    if (!a_knocked_out) return -1;
                    if (!b_knocked_out) return 1;
                });

                var prize_amounts = [40, 10, 5];
                var final_place = 4;
                var prize = 0;
                if (self.tournament_complete) {
                    for (var i = 0; i < self.top_three_teams.length; i++) {
                        if (person.teams.indexOf(self.top_three_teams[i]) >= 0) {
                            final_place = Math.min(final_place, i + 1);
                            prize += prize_amounts[i];
                        }
                    }
                }

                return {
                    name: person.name,
                    teams: teams,
                    final_place: final_place,
                    prize: prize
                }
            });

            people.forEach(function(person) {
                person.competing_team_count = person.teams.reduce(function(accum, team) {
                    return accum + !self.team_knocked_out[team.code]
                }, 0);
                person.total_tournament_wins = person.teams.reduce(function(accumulator, current) {
                    return accumulator + current.tournament_stats.wins;
                }, 0);
            });

            people.sort(function(a, b) {
                if (a.final_place < b.final_place) return -1;
                if (a.final_place > b.final_place) return 1;

                if (a.competing_team_count > b.competing_team_count) return -1;
                if (a.competing_team_count < b.competing_team_count) return 1;

                if (a.total_tournament_wins > b.total_tournament_wins) return -1;
                if (a.total_tournament_wins < b.total_tournament_wins) return 1;
                return 0;
            });

            return people;
        },
        unallocated_teams: function() {
            var self = this;
            var allocated_team_codes = self.people.map(function(person) {
                return person.teams;
            }).reduce(function(a, b) { return a.concat(b); }, []);
            var unallocated_teams = self.teams.filter(function(team) {
                return allocated_team_codes.indexOf(team.code) == -1;
            });
            unallocated_teams.sort(function(a, b) {
                var a_knocked_out = self.team_knocked_out[a.code],
                    b_knocked_out = self.team_knocked_out[b.code];
                if (a_knocked_out == b_knocked_out) return 0;
                if (!a_knocked_out) return -1;
                if (!b_knocked_out) return 1;
            });
            return unallocated_teams;
        },
        teams_by_code: function() {
            var teams = {};
            this.teams.forEach(function(team) {
                teams[team.code] = team;
            });
            return teams;
        },
        team_code_to_person: function() {
            var teams = {};
            this.people.forEach(function(p) {
                p.teams.forEach(function(t) {
                    teams[t] = p;
                });
            });
            return teams;
        },
        groups: function() {
            var self = this,
                groups = {}
            this.teams.forEach(function(team) {
                if (!groups[team.group]) {
                    groups[team.group] = {
                        code: team.group,
                        teams: []
                    };
                }
                groups[team.group].teams.push(team);
            });

            groups = Object.values(groups);
            groups.sort(function(a, b) {
                if (a.code < b.code) return -1;
                if (a.code > b.code) return 1;
                return 0;
            });

            groups.forEach(function(group) {
                group.teams.sort(function(a, b) {
                    // Sort by points
                    var a_points = a.group_stats.get_points(),
                        b_points = b.group_stats.get_points();
                    if (a_points > b_points) return -1;
                    if (a_points < b_points) return 1;

                    // Then by goal difference.
                    var a_gd = a.group_stats.get_goal_difference(),
                        b_gd = b.group_stats.get_goal_difference();
                    if (a_gd > b_gd) return -1;
                    if (a_gd < b_gd) return 1;

                    // Then by goals scored.
                    if (a.group_stats.goals_scored > b.group_stats.goals_scored) return -1;
                    if (a.group_stats.goals_scored < b.group_stats.goals_scored) return 1;

                    // Then by name.
                    if (a.name < b.name) return -1;
                    if (a.name > b.name) return 1;
                    return 0;
                });
            });

            return groups;
        },
        team_knocked_out: function() {
            var self = this,
                team_knocked_out = {},
                simulated_match_count = 0;

            self.teams.forEach(function(team) {
                team_knocked_out[team.code] = false;
            });

            if (!self.matches) {
                // We haven't loaded the matches yet, just return false for everyone.
                return team_knocked_out;
            }

            self.groups.forEach(function(group) {
                var group_future_matches = self.group_matches.filter(function(match) {
                    return match.status != 'completed' && self.teams_by_code[match.home_team.country].group === group.code;
                });
                var team_highest_positions = {}

                if (group_future_matches.length) {
                    // There are matches still to be played, simulate them!
                    var possible_group_match_outcomes = product(['H', 'A', 'D'], group_future_matches.length);

                    possible_group_match_outcomes.forEach(function(match_results) {
                        var group_table = {};
                        group.teams.forEach(function(team) {
                            group_table[team.code] = team.group_stats.get_points();
                        });

                        group_future_matches.forEach(function(match, i) {
                            var outcome = match_results[i];
                            if (outcome == 'H') {
                                group_table[match.home_team.country] += 3;
                            } else if (outcome == 'A') {
                                group_table[match.away_team.country] += 3;
                            } else if (outcome == 'D') {
                                group_table[match.home_team.country]++;
                                group_table[match.away_team.country]++;
                            }
                            simulated_match_count++;
                        });

                        group_table = Object.keys(group_table).map(function(key) {
                            return {team: key, points: group_table[key]};
                        });

                        group_table.sort(function(a, b) {
                            if (a.points > b.points) return -1;
                            if (a.points < b.points) return 1;
                            return 0;
                        });

                        var pos = 1,
                            previous_row_points = group_table[0].points;
                        group_table.forEach(function(row, actual_pos) {
                            actual_pos++;
                            if (row.points < previous_row_points) {
                                pos = actual_pos;
                            }
                            previous_row_points = row.points;

                            if (
                                !team_highest_positions[row.team] ||
                                pos < team_highest_positions[row.team]
                            ) {
                                team_highest_positions[row.team] = pos;
                            }
                        });
                    });
                } else {
                    // There are no matches left to be played in this group, just use their position in the group.
                    group.teams.forEach(function(team, i) {
                        team_highest_positions[team.code] = i + 1;
                    });
                }

                for (var team_code in team_highest_positions) {
                    team_knocked_out[team_code] = (
                        self.teams_by_code[team_code].knocked_out ||
                        team_highest_positions[team_code] > 2
                    );
                }
            });
            if (simulated_match_count) {
                console.log('Simulated ' + simulated_match_count +
                            ' matches to work out teams that have been knocked out.');
            }

            self.knockout_matches.forEach(function(m) {
                // Skip non completed matches.
                if (m.status != 'completed') return;

                if (m.winner_code == m.home_team.country) {
                    team_knocked_out[m.away_team.country] = true;
                } else {
                    team_knocked_out[m.home_team.country] = true;
                }
            });

            return team_knocked_out;
        },
        matches_grouped_by_date: function() {
            if (!this.matches) return null;

            var days = {};

            this.matches.forEach(function(match) {
                var match_date_string = dateString(new Date(match.datetime));
                if (!(match_date_string in days)) {
                    days[match_date_string] = [match];
                } else {
                    days[match_date_string].push(match);
                }
            });

            return days;
        },
        next_date: function() {
            var date = new Date(this.selected_date);
            date.setDate(date.getDate() + 1);
            return dateString(date);
        },
        previous_date: function() {
            var date = new Date(this.selected_date);
            date.setDate(date.getDate() - 1);
            return dateString(date);
        },
        date_range: function() {
            if (!this.matches_grouped_by_date) return this.selected_date;
            var min = this.selected_date;
            var max = this.selected_date;
            for (var date_string in this.matches_grouped_by_date) {
                if (date_string < min) {
                    min = date_string;
                }
                if (date_string > max) {
                    max = date_string;
                }
            }
            return {min: min, max: max};
        },
        can_select_next_date: function() {
            return this.matches_grouped_by_date && this.next_date <= this.date_range.max;
        },
        can_select_previous_date: function() {
            return this.matches_grouped_by_date && this.previous_date >= this.date_range.min;
        },
        loaded_matches: function() {
            return Boolean(this.matches);
        },
        group_matches: function() {
            if (!this.matches) return null;
            return this.matches.filter((m) => m.stage_name === 'First stage');
        },
        knockout_matches: function() {
            if (!this.matches) return null;
            return this.matches.filter((m) => m.stage_name !== 'First stage');
        }
    }
}
</script>


<style>
    body {
        background-color: #111;
        font-family: sans-serif;
        color: #ccc;
        touch-action: manipulation;
    }

    .container {
        max-width: 900px;
        margin: 0 auto;
    }
    .match-day-selector .date {
        display: inline-block;
        text-align: center;
        padding: 0 4px;
    }

    .match-day-selector .date.is-today {
        font-weight: bold;
    }

    .match-day-selector button {
        vertical-align: top;
        background-color: #111;
        color: #ccc;
        height: 36px;
        width: 68px;
        border: 1px solid #ccc;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        cursor: pointer;
    }

    .match-day-selector button:focus {
        outline: none;
        box-shadow: 0px 0px 2px 1px #999;
    }

    .match-day-selector button:active {
        outline: none;
        box-shadow: 0px 0px 4px 2px #999;
    }

    .match-day-selector button:hover {
        background-color: #222;
    }

    .match-day-selector button:disabled {
        background-color: #111;
        border-color: #333;
        color: #333;
        cursor: not-allowed;
    }

    .matches-container {
        padding-top: 8px;
    }

    h2 {
        margin-bottom: 8px;
    }

    .match-header {
        margin-top: 0;
    }

    .match {
        margin-bottom: 20px;
        border-left: 6px solid #333;
        padding-left: 8px;
    }

    @keyframes in-progress-flash {
        from {border-left-color: #333;}
        to {border-left-color: #ccc;}
    }

    .match.in-progress {
        animation-name: in-progress-flash;
        animation-duration: 1s;
        animation-direction: alternate;
        animation-iteration-count: infinite;
        animation-timing-function: ease-out;
    }

    .match.completed {
        border-left-color: #ccc;
    }

    .match .team {
        margin-left: 0;
        margin-right: 0;
    }

    .match .score {
        font-weight: bold;
    }

    table {
        border-collapse: collapse;
    }

    table.player-table {
        width: 100%;
    }

    table.group-table {
        width: 100%;
    }

    .person-row-knocked-out {
        color: #999;
    }

    .person-row-knocked-out .person-name {
        text-decoration: line-through;
    }

    .prize {
        font-weight: bold;
    }

    .final-place-1 .prize {
        color: gold;
    }

    .final-place-2 .prize {
        color: silver;
    }

    .final-place-3 .prize {
        color: #8a4c00;
    }

    @media only screen and (max-width: 500px) {
        .hide-small {
            display: none;
        }
    }

    .col2 {
        width: 50%;
        display: inline-block;
        box-sizing: border-box;
        padding: 8px;
        vertical-align: top;
    }

    .col2:blank {
        display: none;
    }

    @media only screen and (max-width: 990px) {
        .col2 {
            width: 100%;
            padding: 8px 0;
        }
    }

    th, td {
        border: 1px solid #333;
        padding: 8px;
        text-align: left;
    }

    .unallocated-teams {
        margin-top: 16px;
    }

    .team {
        display: inline-block;
        background-color: #333;
        border-radius: 4px;
        padding: 4px;
        white-space: nowrap
    }

    .team-spaced {
        margin: 4px;
    }

    .team.knocked-out {
        text-decoration: line-through;
        background-color: #222;
        color: #999;
    }

    .team .flag {
        /* height: 16px; */
        border-radius: 4px;
    }
    .team.knocked-out .flag {
        filter: brightness(25%)
    }
</style>
