/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import type { ActionFunctionArgs } from "@remix-run/node";
import { authenticate } from "../shopify.server";
import db from "../db.server";
import { AnalyticsInterface, jitsuAnalytics } from "@jitsu/js";
import { transform } from "event_lib/transformer";
import { analytics_state, writeKeyTovalmiAnalyticsMap } from "./analyticsState";
import { deleteValmiConfig, deleteWebPixel, getValmiConfig } from "~/api/prisma.server";

export const action = async ({ request }: ActionFunctionArgs) => {
  const { topic, shop, session, admin, payload } = await authenticate.webhook(
    request
  );

  if (!admin) {
    // The admin context isn't returned if the webhook fired after a shop was uninstalled.
    throw new Response();
  }

  const valmiconf = await getValmiConfig(session.shop);
  if(valmiconf.host && valmiconf.writeKey){
    var valmiAnalytics : AnalyticsInterface = null;

    if (writeKeyTovalmiAnalyticsMap.hasOwnProperty(valmiconf.writeKey)) {
      valmiAnalytics = writeKeyTovalmiAnalyticsMap[valmiconf.writeKey];
    }
    if (!valmiAnalytics) {
      valmiAnalytics = jitsuAnalytics({
        host: valmiconf.host,
        writeKey: valmiconf.writeKey,
        //debug: true,
      });
      writeKeyTovalmiAnalyticsMap[valmiconf.writeKey] = valmiAnalytics; 
    }
    
    // FORCING ANONYMOUS ID
    const storage= (valmiAnalytics as any).storage;
    storage.setItem("__anon_id", "valmi_cloud_event_server");
    const userState =  (valmiAnalytics as any).user();
    if (userState) {
      userState.anonymousId = "valmi_cloud_event_server";
    }
    (valmiAnalytics as any).setAnonymousId("valmi_cloud_event_server");
    //valmiAnalytics.setAnonymousId("valmi_cloud_event_server"); -- WORKING ONLY IN DEBUG MODE
  }
 
  //console.log("webhook", topic, shop, session, payload);
  if (payload) {
    (payload as any)["topic"]=topic;
  }
  const state = analytics_state();
  //console.log("state", state); 

  
  switch (topic) {
    case "APP_UNINSTALLED":
      if (session) {
        await db.session.deleteMany({ where: { shop } });
      }
      break;
    case "CUSTOMERS_DATA_REQUEST":
      throw new Response("{}", { status: 200 });
    case "CUSTOMERS_REDACT":
      throw new Response("Success", { status: 200 });
    case "SHOP_REDACT":
      deleteValmiConfig(session.shop);
      deleteWebPixel(session.shop);
      throw new Response("Success", { status: 200 });
    case "CARTS_CREATE":
    case "CARTS_UPDATE":
    case "CUSTOMERS_CREATE":
    case "CUSTOMERS_UPDATE":
    case "CHECKOUTS_CREATE":
    case "CHECKOUTS_UPDATE":
    case "FULFILLMENTS_CREATE":
    case "FULFILLMENTS_UPDATE":
    case "ORDERS_CREATE":
    case "ORDERS_CANCELLED": 
    case "REFUNDS_CREATE":
      transform(valmiAnalytics, payload, state);
      break;
    
    default:
      // console.log(topic, payload);
      throw new Response("valmi webhook events", { status: 200 });
  }
  throw new Response();
};



