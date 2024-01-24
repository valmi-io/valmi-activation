/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Wednesday, January 3rd 2024, 10:20:04 pm
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

import type { ActionFunctionArgs } from "@remix-run/node";
import { authenticate } from "../shopify.server";
import db from "../db.server";
import { AnalyticsInterface, jitsuAnalytics } from "@jitsu/js";
import { transform } from "event_lib/transformer";
import { analytics_state } from "./analyticsState";
import { getValmiConfig } from "~/api/prisma.server";
var valmiAnalytics : AnalyticsInterface = null;

export const action = async ({ request }: ActionFunctionArgs) => {
  const { topic, shop, session, admin, payload } = await authenticate.webhook(
    request
  );

  if (!admin) {
    // The admin context isn't returned if the webhook fired after a shop was uninstalled.
    throw new Response();
  }

  const valmiconf = await getValmiConfig();
  if( !valmiAnalytics){
    valmiAnalytics = jitsuAnalytics({
      host: valmiconf.host,
      writeKey: valmiconf.writeKey,
    });
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
    case "CUSTOMERS_REDACT":
    case "SHOP_REDACT":
      throw new Response("Unhandled webhook topic", { status: 404 });
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



