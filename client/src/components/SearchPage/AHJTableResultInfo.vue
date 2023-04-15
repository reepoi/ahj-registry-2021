<template>
  <div class="table-info">
    <b-dropdown text="Download Results" class="m-md-2" :disabled="Boolean($store.state.apiErrorInfo.status) || ahjCount === 0">
      <template #button-content>
        <span v-if="resultsDownloading">
          Downloading... (<b-spinner small class="text-center" />
          {{ downloadCompletionPercent }}%)
        </span>
        <span v-else-if="!performedSearch">
          Loading...
        </span>
        <span v-else>
          Download {{ ahjCount }} Results
        </span>
      </template>
      <b-dropdown-item :disabled="resultsDownloading" @click="exportSearchResultsJSONCSV('application/json')">JSON (.json)</b-dropdown-item>
      <b-dropdown-item :disabled="resultsDownloading" @click="exportSearchResultsJSONCSV('text/csv')">CSV (.csv)</b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>

import constants from '../../constants';

export default {
  data() {
    return {
      ahjCount: 0,
      performedSearch: false
    };
  },
  methods: {
    /**
     * call store.js method to download search results
     * @param filetype the file extension requested
     */
    exportSearchResultsJSONCSV(filetype) {
      let state = this.$store.state;
      // do not try to download results if there are no search results
      if (state.resultsDownloading || state.selectedAHJ === null) {
        return;
      }
      let url = `${constants.API_ENDPOINT}ahj-private/`;
      let formatResults = results => results.map(page => page.ahjlist).flat();
      this.$store.commit("exportAPIResultsJSONCSV", { url, search: this.currentSearchQuery, formatResults, filetype });
    }
  },
  computed: {
    /**
     * Helper to say if the search results are still loading
     * @returns {boolean}
     */
    apiLoading() {
      return this.$store.state.apiLoading;
    },
    /**
     * Indicator that results are currently being downloaded
     * @returns {boolean}
     */
    resultsDownloading() {
      return this.$store.state.resultsDownloading;
    },
    /**
     * The current precentage of completion of loading the download
     * @returns {number}
     */
    downloadCompletionPercent() {
      return this.$store.state.downloadCompletionPercent;
    },
    currentSearchQuery() {
      let state = this.$store.state;
      let searchPayload = { ...state.searchedQuery };
      if (state.searchedGeoJSON) {
        searchPayload.FeatureCollection = state.searchedGeoJSON;
      }
      // Tell endpoint to send JSON for user consumption.
      searchPayload.use_public_view = true;
      return searchPayload;
    }
  },
  watch: {
    /**
     * Listener to indicate whether a new search was made
     * @param newValue the new selected ahj, may be null
     */
    '$store.state.apiLoading': function(newValue) {
      if (newValue) { // new search was made
        this.ahjCount = 0;
        this.performedSearch = false;
      } else { // new search is complete
        this.ahjCount = this.$store.state.apiData['count'];
        this.performedSearch = true;
      }
    }
  }
};
</script>

<style scoped>
.table-info {
  display: inline;
}
</style>
