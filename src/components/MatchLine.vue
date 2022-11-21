<template>
  <div
    class="match"
    :class="{
      'in-progress': match.status == 'in_progress',
      completed: match.status == 'completed',
    }"
  >
    <template v-if="match">
      <TeamBadge
        :team="teams_by_code[match.home_team.country] || null"
        :person="team_code_to_person[match.home_team.country]"
        class="team-spaced"
      />
      <span v-if="show_scores" class="score">
        {{ match.home_team.goals }}
      </span>
      <template v-if="show_scores">–</template><template v-else>vs</template>
      <span v-if="show_scores" class="score">
        {{ match.away_team.goals }}
      </span>
      <TeamBadge
        :team="teams_by_code[match.away_team.country] || null"
        :person="team_code_to_person[match.away_team.country]"
        class="team-spaced"
      />
      <div v-if="show_penalties">
        <small class="in-progress-penalties">
          <strong
            >{{ match.home_team.penalties }} –
            {{ match.away_team.penalties }}</strong
          >
          on penalties
        </small>
      </div>
      <div class="match-kickoff">
        <small>{{ formatted_kickoff_time }} ({{ tz_offset }})</small>
      </div>
    </template>
    <p v-else>n/a</p>
  </div>
</template>

<script>
import TeamBadge from "./TeamBadge.vue";

import { pad2 } from "../utils.js";

export default {
  components: {
    TeamBadge,
  },
  props: {
    match: Object,
    loading: Boolean,
    teams_by_code: Object,
    team_code_to_person: Object,
  },
  data: function () {
    var tz_offset = -new Date().getTimezoneOffset();
    tz_offset =
      "GMT" +
      (tz_offset >= 0 ? "+" : "-") +
      pad2(Math.floor(Math.abs(tz_offset) / 60)) +
      ":" +
      pad2(Math.abs(tz_offset) % 60);
    return {
      tz_offset: tz_offset,
    };
  },
  computed: {
    show_scores: function () {
      if (!this.match) {
        return false;
      }
      return (
        this.match.status == "in_progress" || this.match.status == "completed"
      );
    },
    show_penalties: function () {
      return (
        this.show_scores &&
        this.match.home_team.penalties + this.match.away_team.penalties > 0
      );
    },
    formatted_kickoff_time: function () {
      if (!this.match) {
        return null;
      }
      var months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
      ];
      var t = new Date(this.match.datetime);
      return (
        months[t.getMonth()] +
        " " +
        t.getDate() +
        " " +
        +pad2(t.getHours()) +
        ":" +
        pad2(t.getSeconds())
      );
    },
  },
};
</script>
