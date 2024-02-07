/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import {register} from "@shopify/web-pixels-extension";
import {jitsuAnalytics} from "@jitsu/js";
import {transform} from "../../../event_lib/transformer";
import { v4 as uuidv4 } from 'uuid';

register(({ analytics, browser, init, settings}) => {
  const valmiAnalytics = jitsuAnalytics({
    host: settings.host,  
    writeKey: settings.writeKey,
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
