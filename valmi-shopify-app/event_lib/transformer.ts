/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Thursday, January 11th 2024, 11:55:55 am
 * Author: Rajashekar Varkala @ valmi.io
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { setDataForJsonPath, query} from "./jp";
import { AnalyticsInterface } from "@jitsu/js";
import {event_handlers} from './event';
import { ignoreIfEmpty } from "./common";

/*const path = "$.store.book[*].author.n";
console.log("path", path);
//const mappeddata = { store: { book: [ {author: { b: "x" }},{author: { b: "y" }}] } } ;
const mappeddata = {};
setDataForJsonPath(["x"], mappeddata, path);
console.log("mappeddata", JSON.stringify(mappeddata));
*/
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
        const { to, beforeUpdate } = obj[key];
        const value =  query(pixel_event, key);
        //console.log("value", value);
        if (beforeUpdate === undefined ||beforeUpdate(value)) {
            setDataForJsonPath(value??[], event, to);
        }
    }); 
    const cmapping: any = event_mapping();
    cmapping.forEach((obj: any) => {
      const key = Object.keys(obj)[0];
        const { to, beforeUpdate } = obj[key];
        const value = query(pixel_event, key);
        if(key.endsWith("phone")){
          console.log("beforeupdate", beforeUpdate(value) , key, value);
        }
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
  console.log(JSON.stringify(ret));
  // make the call
  ret.forEach((element:any) => {
    console.log("element", element);
    element["method"]?.(element["args"]);
  });
};
