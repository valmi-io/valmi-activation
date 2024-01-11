import { setDataForJsonPath, query} from "./jp";
import { AnalyticsInterface } from "@jitsu/js";
import {event_handlers} from './event';

/*const path = "$.store.book[*].author.n";
console.log("path", path);
//const mappeddata = { store: { book: [ {author: { b: "x" }},{author: { b: "y" }}] } } ;
const mappeddata = {};
setDataForJsonPath(["x"], mappeddata, path);
console.log("mappeddata", JSON.stringify(mappeddata));
*/
const default_mapping = (): any => {
  return {
    "$.clientId": {
      to: "$.clientId",
      //return to continue updating, false to stop updating
      beforeUpdate: (value: any) => {
        return value == null || value == undefined ? false : true;
      },
    },
  };
};

const stage_map = (valmiAnalytics: AnalyticsInterface, event: any, pixel_event: any, event_mapping: any): any => {
    const mapping = default_mapping(); 
    Object.keys(mapping).forEach((key) => {
        const { to, beforeUpdate } = mapping[key];
        const value =  query(pixel_event, key);
        console.log("value", value);
        if (beforeUpdate == undefined ||beforeUpdate(value)) {
            setDataForJsonPath(value??[""], event, to);
        }
    }); 
    const cmapping: any = event_mapping();
    Object.keys(cmapping).forEach((key) => {
        const { to, beforeUpdate } = cmapping[key];
        const value = query(pixel_event, key);
        if (beforeUpdate == undefined || beforeUpdate(value)) {
            setDataForJsonPath(value??[""], event, to);
        }
    });
    return event;
};

const stage_prepare = (valmiAnalytics: AnalyticsInterface, pixel_event: any): any => {
  return {};
};

const analytics_call = (
  valmiAnalytics: AnalyticsInterface,
  pixel_event: any
): any => {
  const {fn,mapping} = event_handlers(valmiAnalytics, pixel_event);
  return {
    method: fn,
    args: [stage_map(valmiAnalytics, stage_prepare(valmiAnalytics,pixel_event), pixel_event,mapping)],
  };
};

export const transform = (
  valmiAnalytics: AnalyticsInterface,
  pixel_event: any
): any => {
  const ret = analytics_call(
    valmiAnalytics,
    pixel_event
  );
  console.log(JSON.stringify(ret));
  // make the call
  ret["method"]?.(...ret["args"]);
};
