<template>
  <div class="team" :class="{ 'knocked-out': knocked_out }">
    <template v-if="team">
      {{ team.name }}
      <template v-if="show_person">
        <template v-if="person"> ({{ person.name }}) </template>
        <template v-else> (N/A) </template>
      </template>
      <!-- <img :src="get_flag_url(team.code)" width="16" height="12" class="flag"> -->
      <img :src="get_flag_url(team.code)" height="16" class="flag" />
    </template>
    <template v-else> n/a </template>
  </div>
</template>

<script>
const fifa_to_iso = {
  QAT: "qa",
  ECU: "ec",
  SEN: "sn",
  NED: "nl",
  ENG: "gb-eng",
  IRN: "ir",
  USA: "us",
  WAL: "gb-wls",
  ARG: "ar",
  KSA: "sa",
  MEX: "mx",
  POL: "pl",
  FRA: "fr",
  AUS: "au",
  DEN: "dk",
  TUN: "tn",
  ESP: "es",
  CRC: "cr",
  GER: "de",
  JPN: "jp",
  BEL: "be",
  CAN: "cn",
  MAR: "ma",
  CRO: "hr",
  BRA: "br",
  SRB: "rs",
  SUI: "ch",
  CMR: "cm",
  POR: "pt",
  GHA: "gh",
  URU: "uy",
  KOR: "kr",
};

// function get_flag_url(fifa_country_code) {
//     const iso_country_code = fifa_to_iso[fifa_country_code] ?? 'xx';
//     return `https://flagcdn.com/16x12/${iso_country_code}.png`
// }

function get_flag_url(fifa_country_code) {
  const iso_country_code = fifa_to_iso[fifa_country_code] ?? "xx";
  return `https://flagcdn.com/h20/${iso_country_code}.png`;
}

export default {
  props: {
    team: Object,
    person: Object,
    show_person: {
      type: Boolean,
      default: true,
    },
    knocked_out: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    get_flag_url,
  },
};
</script>
