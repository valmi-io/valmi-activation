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
import JSONPath from "jsonpath";

const setDataAtCurrentPath = (
  sourcedata: any[],
  mappeddata: any,
  currentPath: any[],
  arrayIdx: number,
  key: string
) => {
  if (sourcedata.length > 0) {
    let x = [mappeddata];
    for (let i = 0; i < currentPath.length; i++) {
      x = x.flatMap((obj) => {
        return obj[currentPath[i]];
      });
    }
    for (let i = 0; i < x.length; i++) {
      if (sourcedata.length <= i) {
        x[i][key] = {}; // setting empty object
      } else {
        x[i][key] = sourcedata[i];
      }
    }
  }
};

const checkForPropertyAtPath = (
  mappeddata: any,
  currentPath: any[],
  arrayIdx: number,
  key: string
) => {
  // go to the end
  let x = mappeddata;
  for (let i = 0; i < currentPath.length; i++) {
    console.log(key, x, currentPath);
    if (arrayIdx == i) {
      x = x[currentPath[i]][0];
    } else {
      x = x[currentPath[i]];
    }
  }
  if (x.hasOwnProperty(key)) return true;
  return false;
};

// build the mappeddata structure --  only one wildcard supported.
const setDataForJsonPath = (
  sourcedata: any[],
  mappeddata: any,
  pathexp: string
) => {
  var path = JSONPath.parse(pathexp);

  const currentPath = [];
  let arrayIdx = -1;
  for (var idx = 0; idx < path.length; idx++) {
    const element = path[idx];
    if (element.expression.type == "identifier") {
      if (idx < path.length - 1) {
        if (
          checkForPropertyAtPath(
            mappeddata,
            currentPath,
            arrayIdx,
            element.expression.value
          )
        ) {
        } else {
          if (
            idx < path.length - 1 &&
            path[idx + 1].expression.type == "wildcard" &&
            path[idx + 1].expression.value == "*"
          ) {
            setDataAtCurrentPath(
              [
                sourcedata.map((el) => {
                  return {};
                }),
              ], //setting an  array with empty objects
              mappeddata,
              currentPath,
              arrayIdx,
              element.expression.value
            );
          } else {
            setDataAtCurrentPath(
              [{}], //setting an empty object
              mappeddata,
              currentPath,
              arrayIdx,
              element.expression.value
            );
          }
        }
        currentPath.push(element.expression.value);
      } else {
        setDataAtCurrentPath(
          sourcedata,
          mappeddata,
          currentPath,
          arrayIdx,
          element.expression.value
        );
      }
    } else if (
      element.expression.type == "wildcard" &&
      element.expression.value == "*"
    ) {
      arrayIdx = currentPath.length - 1;
    }
  }
};

const path = "$.store.book.author[*].n";
console.log("path", path);
const mappeddata = { store: { book: { author: [{ b: "x" }, { b: "y" }] } } };
//const mappeddata = {};
setDataForJsonPath(["x", "y"], mappeddata, path);
console.log("mappeddata", JSON.stringify(mappeddata));

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
