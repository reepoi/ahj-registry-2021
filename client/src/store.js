/*
 * A Vuex store is a global state for the web application.
 * It has variables and methods that can be accessed from
 * all components and views.
 *
 * Mutations, the methods of the store, are similar to creating Promises.
 *
 * To modify a variable in the store, be sure to call the relevant mutation
 * or create a new one. New mutation methods take up to two arguments: state; custom arg
 *
 * Access these store variables in elsewhere using 'this.$store.state.<variable_name>'
 * Call mutations with:
 *  - 'this.$store.commit("<mutation_name>");
 *  - 'this.$store.commit("<mutation_name>", <custom_arg>);'
 */
import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";
import createPersistedState from 'vuex-persistedstate';
import constants from "./constants";
import * as utils from "./utils.js"


Vue.use(Vuex);

export default new Vuex.Store({
  plugins: [createPersistedState({ // Keeps logged in users logged in over page reloads
    paths: ['authToken'],
    storage: window.localStorage,
})],
state: {
    apiData: [], // stores results of ahj search page
    currentAHJ: null, // Current AHJ in focus on map and AHJ table
    cancelAPICallToken: null, // Field to call .cancel() on to cancel an axios api request
    apiLoading: true,
    apiError: false,
    apiErrorInfo: { status: null, msg: ''},
    showTable: false, // shows the search results table
    selectedAHJ: null, // Current AHJ in focus on map and AHJ table
    editList: null,
    authToken: "", // auth token of the current logged in user; used to call apis when user is logged in
    currentUserInfo: null, // info of user currently logged in (not saved after page reload)
    searchedQuery: null, // query entered on ahj search page
    searchedGeoJSON: null, // query of region drawn on map

    // Controls interface for downloading results
    resultsDownloading: false, // Enables or disables download results button
    downloadCompletionPercent: 0, // Updates downloading progress of results
},
    getters: {
        apiData: state => state.apiData,
        loggedIn: state => state.authToken !== "",
        authToken: state => "Token " + state.authToken, // gets webpage's webpage api token or currently logged in api token
        currentUserInfo: state => state.currentUserInfo,
    },
    mutations: {
        callAPI(state, queryPayload) {
            state.apiLoading = true;
            state.apiData = [];
            state.apiErrorInfo = { status: null, msg: '' }
            if (!state.showTable) {
                state.showTable = true;
            }
            // If another axios request has been made; cancel it
            if (state.cancelAPICallToken !== null) {
                state.cancelAPICallToken("previous request cancelled");
            }
            let url = `${constants.API_ENDPOINT}ahj-private/?`;

            // save query for other components to modify and perform current search later
            if (queryPayload) {
                state.searchedQuery = queryPayload;
            }

            // track what page of results is being searched
            if (queryPayload['Pagination']) {
                url += queryPayload['Pagination'];
            }

            // check if there was a region searched
            if (state.searchedGeoJSON) {
                queryPayload['FeatureCollection'] = state.searchedGeoJSON;
            }
            let headers = {};
            if (this.getters.loggedIn) {
                headers.Authorization = this.getters.authToken;
            }
            axios
                .post(url, queryPayload, {
                    headers: headers,
                    cancelToken: new axios.CancelToken(function executor(c) {
                        state.cancelAPICallToken = c;
                    })
                })
                .then(response => {
                    state.apiData = response.data;
                    state.cancelAPICallToken = null;
                    state.apiLoading = false;

                    // select first ahj in results as focus if results were returned
                    if (state.apiData.count > 0) {
                        state.selectedAHJ = state.apiData.results.ahjlist[0];
                    }
                })
                .catch((err) => {
                    // request was cancelled or some other error
                    if(err.message !== 'previous request cancelled'){
                        state.apiErrorInfo = utils.axiosGetAPIErrorInfo(err);
                        state.apiLoading = false;
                    }
                });
        },
        /**
         * Retrieves one AHJ and sets it to state.apiData with
         * the same structure as callAPI.
         * @param state
         * @param params an object with these entries:
         * {
         *     AHJPK: (required),
         *     view: one of the values in constant.js CHOICE_FIELDS APIEditViewMode (optional)
         * }
         */
        callAPISingleAHJ(state, params) {
            let headers = {};
            if (this.getters.loggedIn) {
                headers.Authorization = this.getters.authToken;
            }
            axios.get(`${constants.API_ENDPOINT}ahj-one/`,
                { params: params,
                  headers: headers})
                .then(response => { state.apiData = { results: { ahjlist: [response.data] } }; })
                .catch(err => { state.apiErrorInfo = utils.axiosGetAPIErrorInfo(err); });
        },
        setSelectedAHJ(state, ahj) {
            state.selectedAHJ = ahj;
        },
        setSearchGeoJSON(state, geojson) {
            state.searchedGeoJSON = geojson;
        },
        setShowTable(state, payload) {
            state.showTable = payload;
        },
        /**
         * Export API results from a POST API endpoint using Django's LimitOffsetPaginator as a JSON or CSV file.
         * This updates the state's:
         *  - resultsDownloading: boolean,
         *  - downloadCompletionPercent: float,
         *  - apiErrorInfo: object in case of error
         * @param state
         * @param query an object with these entries:
         * {
         *     url: the API endpoint,
         *     search: the search parameter object to be POSTed,
         *     formatResults: a function to format the results from the API before download,
         *     filename: string,
         *     filetype: the type of the file to be downloaded (JSON/CSV)
         * }
         */
        exportAPIResultsJSONCSV(state, query) {
          state.resultsDownloading = true;
          let headers = {};
          if (this.getters.loggedIn) {
            headers.Authorization = this.getters.authToken;
          }
          let setCompletionPercent = (totalResults, offsetComplete) => { state.downloadCompletionPercent = (offsetComplete / totalResults * 100).toFixed(); };
          utils.gatherAllPaginatedAPIResults({ url: query.url, headers, search: query.search, offsetStep: 20, setCompletionPercent })
            .then(results => {
              results = query.formatResults ? query.formatResults(results) : results;
              utils.downloadFile({ data: results, filename: query.filename, filetype: query.filetype });
              state.resultsDownloading = false;
              state.downloadCompletionPercent = 0;
            })
            .catch(err => {
              state.apiErrorInfo = utils.axiosGetAPIErrorInfo(err);
              state.resultsDownloading = false;
              state.downloadCompletionPercent = 0;
            });
        },
        changeAuthToken(state, authToken) {
            state.authToken = authToken;
        },
        changeCurrentUserInfo(state, payload) {
            state.currentUserInfo = payload;
        },
        getEdits(state, query){
            let headers = {};
            if (this.getters.loggedIn) {
                headers.Authorization = this.getters.authToken;
            }
            axios.get(`${constants.API_ENDPOINT}edit/?${query}`,
                { headers: headers,
                  cancelToken: new axios.CancelToken(function executor(c) {
                      state.cancelAPICallToken = c;
                  })
                })
                .then(response => {
                    state.editList = response.data;
                    state.cancelAPICallToken = null;
                    state.apiLoading = false;
                })
        },
        resetAPIErrorInfo(state) {
            state.apiErrorInfo = { status: null, msg: '' }
        },
        clearState(state){ // reset fields in the store
            state.callData = [];
            state.leafletMap = null;
            state.leafletMarker = null;
            state.polygons = null;
            state.currPolyInd = null;
            state.apiLoading = true;
            state.mapViewCenter = [34.05, -118.24];
        }
    },
    actions: {
        async getUserInfo({getters, commit}){ // get currently logged in user's info by their webpage auth token
            let query = constants.API_ENDPOINT + "user/active/";
            await axios.get(query, {
                headers: {
                    Authorization: getters.authToken
                }
            })
                .then(async (response) => {
                    let userInfo = response.data;
                    commit('changeCurrentUserInfo', userInfo);
                });
        }
    },
});
