<template>
  <div class="group-table-container col2">
    <table class="group-table">
      <thead>
        <tr>
          <th colspan="6">Group {{ group.code }}</th>
        </tr>
        <tr>
          <th>Team</th>
          <th class="hide-small">W</th>
          <th class="hide-small">D</th>
          <th class="hide-small">L</th>
          <th class="hide-small">GD</th>
          <th>Pts</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="team in group.teams" :key="team.code">
          <td>
            <TeamBadge
              :team="teams_by_code[team.code] || null"
              :person="team_code_to_person[team.code]"
              :knocked_out="team_knocked_out[team.code]"
              class="team-spaced"
            />
          </td>
          <td class="hide-small">
            {{ loaded_matches ? team.group_stats.wins : "?" }}
          </td>
          <td class="hide-small">
            {{ loaded_matches ? team.group_stats.draws : "?" }}
          </td>
          <td class="hide-small">
            {{ loaded_matches ? team.group_stats.losses : "?" }}
          </td>
          <td class="hide-small">
            <template v-if="loaded_matches">
              <template v-if="team.group_stats.get_goal_difference() >= 0"
                >+</template
              >{{ team.group_stats.get_goal_difference() }}
            </template>
            <template v-else> ? </template>
          </td>
          <td>{{ loaded_matches ? team.group_stats.get_points() : "?" }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import TeamBadge from "./TeamBadge.vue";

export default {
  components: {
    TeamBadge,
  },
  props: {
    group: Object,
    teams_by_code: Object,
    team_code_to_person: Object,
    team_knocked_out: Object,
    loaded_matches: Boolean,
  },
};
</script>
