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

import "@shopify/shopify-app-remix/adapters/node";
import {
  AppDistribution,
  DeliveryMethod,
  shopifyApp,
  LATEST_API_VERSION,
} from "@shopify/shopify-app-remix/server";
import { PrismaSessionStorage } from "@shopify/shopify-app-session-storage-prisma";
import { restResources } from "@shopify/shopify-api/rest/admin/2023-10";
import prisma from "./db.server";
import { transform } from "event_lib/transformer";

const obj = {
  "id": "sh-f7c5e721-6971-4DED-1DEE-FAD710538DC1",
  "name": "page_viewed",
  "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
  "timestamp": "2024-01-11T09:06:30.490Z",
  "context": { 
      "document": {
          "location": {
              "href": "https://quickstart-6ebc0909.myshopify.com/products/the-collection-snowboard-liquid",
              "hash": "",
              "host": "quickstart-6ebc0909.myshopify.com",
              "hostname": "quickstart-6ebc0909.myshopify.com",
              "origin": "https://quickstart-6ebc0909.myshopify.com",
              "pathname": "/products/the-collection-snowboard-liquid",
              "port": "",
              "protocol": "https:",
              "search": ""
          },
          "referrer": "https://quickstart-6ebc0909.myshopify.com/",
          "characterSet": "UTF-8",
          "title": "The Collection Snowboard: Liquid – Quickstart (6ebc0909)"
      },
      "navigator": {
          "language": "en-GB",
          "cookieEnabled": true,
          "languages": [
              "en-GB",
              "en-US",
              "en"
          ],
          "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      },
      "window": {
          "innerHeight": 688,
          "innerWidth": 617,
          "outerHeight": 775,
          "outerWidth": 1235,
          "pageXOffset": 0,
          "pageYOffset": 0,
          "location": {
              "href": "https://quickstart-6ebc0909.myshopify.com/products/the-collection-snowboard-liquid",
              "hash": "",
              "host": "quickstart-6ebc0909.myshopify.com",
              "hostname": "quickstart-6ebc0909.myshopify.com",
              "origin": "https://quickstart-6ebc0909.myshopify.com",
              "pathname": "/products/the-collection-snowboard-liquid",
              "port": "",
              "protocol": "https:",
              "search": "" 
          }, 
          "origin": "https://quickstart-6ebc0909.myshopify.com",
          "screen": {
              "height": 800,
              "width": 1280
          },
          "screenX": 0,
          "screenY": 25,
          "scrollX": 0,
          "scrollY": 0
      }
  }
}; 
const fn  = {page:() =>{

}};
transform(fn,obj);

export const valmiHooks: any = {
  APP_UNINSTALLED: {
    deliveryMethod: DeliveryMethod.Http,
    callbackUrl: "/webhooks",
  },
  CARTS_CREATE: {
    deliveryMethod: DeliveryMethod.Http,
    callbackUrl: "/webhooks",
  },
  CARTS_UPDATE: {
    deliveryMethod: DeliveryMethod.Http,
    callbackUrl: "/webhooks",
  },
  CUSTOMERS_CREATE: {
    deliveryMethod: DeliveryMethod.Http,
    callbackUrl: "/webhooks",
  },
  CHECKOUTS_CREATE: {
    deliveryMethod: DeliveryMethod.Http,
    callbackUrl: "/webhooks",
  },
};

const shopify = shopifyApp({
  apiKey: process.env.SHOPIFY_API_KEY,
  apiSecretKey: process.env.SHOPIFY_API_SECRET || "",
  apiVersion: LATEST_API_VERSION,
  scopes: process.env.SCOPES?.split(","),
  appUrl: process.env.SHOPIFY_APP_URL || "",
  authPathPrefix: "/auth",
  sessionStorage: new PrismaSessionStorage(prisma),
  distribution: AppDistribution.AppStore,
  restResources,
  webhooks: valmiHooks,
  hooks: {
    afterAuth: async ({ session }) => {
      shopify.registerWebhooks({ session });
    },
  },
  future: {
    v3_webhookAdminContext: true,
    v3_authenticatePublic: true,
  },
  ...(process.env.SHOP_CUSTOM_DOMAIN
    ? { customShopDomains: [process.env.SHOP_CUSTOM_DOMAIN] }
    : {}),
});

export default shopify;
export const apiVersion = LATEST_API_VERSION;
export const addDocumentResponseHeaders = shopify.addDocumentResponseHeaders;
export const authenticate = shopify.authenticate;
export const unauthenticated = shopify.unauthenticated;
export const login = shopify.login;
export const registerWebhooks = shopify.registerWebhooks;
export const sessionStorage = shopify.sessionStorage;
export const apiUrl = process.env.SHOPIFY_APP_URL || "";
