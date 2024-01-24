/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Wednesday, January 3rd 2024, 10:41:59 pm
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

import {register} from "@shopify/web-pixels-extension";
import {jitsuAnalytics} from "@jitsu/js";
import {transform} from "../../../event_lib/transformer";
import { v4 as uuidv4 } from 'uuid';

register(({ analytics, browser, init, settings}) => {
  const valmiAnalytics = jitsuAnalytics({
    host: settings.host,  
    writeKey: settings.writeKey,
    debug: true,
  }); 
  browser.cookie.get('valmiAnonymousId').then((valmiAnonymousId) => {
    if (valmiAnonymousId) {
      // FORCING ANONYMOUS ID
      const storage= (valmiAnalytics as any).storage;
      storage.setItem("__anon_id", valmiAnonymousId);
      const userState =  (valmiAnalytics as any).user();
      if (userState) {
        userState.anonymousId = valmiAnonymousId;
      }
      (valmiAnalytics as any).setAnonymousId(valmiAnonymousId);

      // valmiAnalytics.setAnonymousId(uuid.toString());-- WORKING ONLY IN DEBUG MODE


    }
    else {
      const uuid = uuidv4().toString();

      // FORCING ANONYMOUS ID
      const storage= (valmiAnalytics as any).storage;
      storage.setItem("__anon_id", uuid);
      const userState =  (valmiAnalytics as any).user();
      if (userState) {
        userState.anonymousId = uuid;
      }
      (valmiAnalytics as any).setAnonymousId(uuid);

      // valmiAnalytics.setAnonymousId(uuid.toString());-- WORKING ONLY IN DEBUG MODE
      
      browser.cookie.set('valmiAnonymousId', uuid.toString()).then(() => {
        console.log("valmiAnonymousId cookie set");
      });
    }
  });
  // Subscribe to events
  analytics.subscribe('all_events', (event) => {

    //console.log("event",event);
    //console.log("cofiguration", settings);
    // To capture PAYMENT FAILED event, we need to credit the theme app extension and edit the liquid file.
    // And then publish a custom pixel event and then subscribe to it on the custom pixel .
    // https://shopify.dev/docs/api/admin-graphql/2024-04/mutations/webPixelCreate
    // https://help.shopify.com/en/manual/promoting-marketing/pixels/custom-pixels/code
    // https://help.shopify.com/en/manual/promoting-marketing/pixels/custom-pixels#custom-pixel-setup

    transform(valmiAnalytics, event, {});
  });
});
