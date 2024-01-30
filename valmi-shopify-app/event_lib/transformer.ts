/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { setDataForJsonPath, query} from "./jp";
import { AnalyticsInterface } from "@jitsu/js";
import {event_handlers} from './event';
import { ignoreIfEmpty } from "./common";

const default_mapping = (): any => {
  return [{
    "$.clientId": {
      to: "$.clientId",
      //return to continue updating, false to stop updating
      beforeUpdate: ignoreIfEmpty,
    },
  }];
};

const stage_map = (valmiAnalytics: AnalyticsInterface, event: any, pixel_event: any, event_mapping: any): any => {
    const mapping = default_mapping(); 
    mapping.forEach((obj: any) => {
        const key = Object.keys(obj)[0];
        // UGLY HACK - had to stop the shopify marathon
        let value = null;
        if(! key.startsWith("$.")){
          value = [key];
        } else {
          value =  query(pixel_event, key);
        }
        const { to, beforeUpdate } = obj[key];
        //console.log("value", value);
        if (beforeUpdate === undefined ||beforeUpdate(value)) {
            setDataForJsonPath(value??[], event, to);
        }
    }); 

    const cmapping: any = event_mapping();
    cmapping.forEach((obj: any) => {
        const key = Object.keys(obj)[0];
        // UGLY HACK - had to stop the shopify marathon
        let value = null;
        if(! key.startsWith("$.")){
          value = [key];
        } else {
          value =  query(pixel_event, key);
        }
        const { to, beforeUpdate } = obj[key];
        if (beforeUpdate === undefined || beforeUpdate(value)) {
            setDataForJsonPath(value??[], event, to);
        }
    });
    return event;
};

const stage_prepare = (valmiAnalytics: AnalyticsInterface, pixel_event: any): any => {
  return {};
};

const analytics_call = (
  valmiAnalytics: AnalyticsInterface,
  pixel_event: any,
  analytics_state: any,
): any => {
  const gen_events = event_handlers(valmiAnalytics, pixel_event, analytics_state);
  return gen_events.map(({fn , data, mapping} : any) => {return {
    method: fn,
    args: stage_map(valmiAnalytics, stage_prepare(valmiAnalytics,data), data,mapping),
  }}); 
};

export const transform = (
  valmiAnalytics: AnalyticsInterface,
  pixel_event: any,
  analytics_state: any,
): any => {
  const ret = analytics_call(
    valmiAnalytics,
    pixel_event,
    analytics_state,
  );
  //console.log(JSON.stringify(ret));
  // make the call
  ret.forEach((element:any) => {
    //console.log("element", element);
    element["method"]?.(element["args"]);
  });
};
