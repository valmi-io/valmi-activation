/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Thursday, January 11th 2024, 1:28:37 pm
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

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = () : any => {
    return [
      {"$.context.document.title":{to: "$.title"}},
      {"$.context.document.location.href": {to: "$.url"}},
      {"$.context.document.referrer": {to: "$.referrer"}},
      {"$.context.document.location.pathname": {to: "$.path"}},
      {"$.context.document.location.search": {to: "$.search"}},
    ];
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.page;


const src = {
  "id": "sh-fbeff139-B180-4A69-2525-807A04088750",
  "name": "page_viewed",
  "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
  "timestamp": "2024-01-12T04:30:54.751Z",
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

const dest = {
  "type": "page",
  "properties": {
      "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
      "title": "The Collection Snowboard: Liquid – Quickstart (6ebc0909)",
      "url": "https://quickstart-6ebc0909.myshopify.com/products/the-collection-snowboard-liquid",
      "referrer": "https://quickstart-6ebc0909.myshopify.com/",
      "path": "/products/the-collection-snowboard-liquid",
      "search": ""
  },
  "userId": null,
  "anonymousId": "137398c1-0672-4e6b-8afc-b99403a0e6ee",
  "timestamp": "2024-01-12T04:30:54.951Z",
  "sentAt": "2024-01-12T04:30:54.951Z",
  "messageId": "lpqr7i7oi4rdx1d7umpp",
  "writeKey": "Yze5gDoyX2w8Kk5doGK0qF59sF6CHxkJ:***",
  "context": {
      "library": {
          "name": "@jitsu/js",
          "version": "0.0.0"
      },
      "traits": {},
      "page": {
          "path": "/products/the-collection-snowboard-liquid",
          "title": "The Collection Snowboard: Liquid – Quickstart (6ebc0909)",
          "url": "https://quickstart-6ebc0909.myshopify.com/products/the-collection-snowboard-liquid"
      },
      "clientIds": {},
      "campaign": {}
  }
};