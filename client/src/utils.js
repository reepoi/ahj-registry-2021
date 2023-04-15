import {createObjectCsvStringifier} from 'csv-writer';
import FileSaver from 'file-saver';
import axios from 'axios';

export function flattenJSON(json, exclude_empty_obj_arrays) {
  let result = {};

  // function to walk the json object
  function recurse(cur, prop) {
    if (Object(cur) !== cur) {
      result[prop] = cur;
    } else if (Array.isArray(cur)) {
      let l = cur.length;
      for (let i = 0; i < l; i++) recurse(cur[i], prop + "[" + i + "]");
      if (l === 0 && !exclude_empty_obj_arrays) result[prop] = [];
    } else {
      let isEmpty = true;
      for (let p in cur) {
        isEmpty = false;
        recurse(cur[p], prop ? prop + "." + p : p);
      }
      if (isEmpty && prop && !exclude_empty_obj_arrays) result[prop] = {};
    }
  }

  recurse(json, "");
  return result;
}

export function jsonToCSV(json) {
  // Create a unique set of column names for all included fields in the array of AHJs
  let flatJSON = flattenJSON(json, true);
  let keys = Object.keys(flatJSON);
  if (Array.isArray(json)) {
    keys = Array.from(new Set(keys.map(key => key.substring(key.indexOf('.') + 1))));
  } else {
    json = [json];
  }
  if (keys.length === 0) {
      return '';
  }
  const csvStringifier = createObjectCsvStringifier({ header: keys.map(key => { return {id: key, title: key }}) });
  let csv_rows = json.map(line => {
    return keys.reduce((result, key) => {
      result[key] = key.split(/[[\].]/)
          .filter(i => i !== '')
          .reduce((o, i) => Object.prototype.hasOwnProperty.call(o, i) ? o[i] : '', line);
      return result;
    }, {});
  });
  return csvStringifier.getHeaderString() + csvStringifier.stringifyRecords(csv_rows);
}

export function gatherAllPaginatedAPIResults({ url, headers, search, offsetStep, updateProgressCallback }) {
  if (!updateProgressCallback) {
    updateProgressCallback = () => {};
  }
  return new Promise((resolve, reject) => {
    let gatherAllObjects = ({url, headers, search, accumulator, offset}) => {
      if (url === null) {
        updateProgressCallback(accumulator.length, offset);
        resolve(accumulator);
      } else {
        axios
          .post(url,
              search,
              {headers: headers})
          .then(response => {
            accumulator = accumulator.concat(response.data.results); // the django rest framework pagination configuration
            offset += offsetStep;
            updateProgressCallback(response.data.count, offset);
            gatherAllObjects({ url: response.data.next, headers, search, accumulator, offset });
          })
          .catch(err => {
            reject(err);
          });
      }
    };
    gatherAllObjects({ url, headers, search, accumulator: [], offset: 0 })
  });
}

export function downloadFile({ data, filename, filetype }) {
  filename = filename || `${new Date().toUTCString()}_results`;
  let fileToExport;
  if (filetype === "application/json") {
    fileToExport = JSON.stringify(data, null, 2);
    filename += ".json";
  } else if (filetype === "text/csv") {
    fileToExport = jsonToCSV(data);
    filename += ".csv";
  }
  FileSaver.saveAs(new Blob([fileToExport], { type: filetype }), filename);
}

export function axiosGetAPIErrorInfo(error) {
  // if (error.isAxiosError) {
  //   return { status: 500, msg: 'Webpage Error' };
  // } else {
  //   return { status: error.response.status, msg: error.response.statusText };
  // }
  return { status: error.response.status, msg: error.response.statusText };
}
