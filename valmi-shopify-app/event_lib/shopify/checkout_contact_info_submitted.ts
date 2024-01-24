/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 11:00:17 am
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
import {ignoreIfEmpty} from '../common';
import { mapping as checkout_mapping } from "./checkout_started";

export const mapping = () : any => {
    return [
      {"$.data.checkout.email":{to: "$.email", beforeUpdate: ignoreIfEmpty}},
      {"$.data.checkout.phone": {to: "$.phone", beforeUpdate: ignoreIfEmpty}},
    ];
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.identify;


export const track_mapping = (): any => {
    const arr = checkout_mapping();
    arr.push(
      {"contact_info_submitted": { to: "$.step" }  },
    )
    return arr;
  };
  
/*
{
    "anonymousId": "507f191e810c19729de860ea",
    "channel": "browser",
    "context": {
      "ip": "8.8.8.8",
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36"
    },
    "integrations": {
      "All": false,
      "Mixpanel": true,
      "Salesforce": true
    },
    "messageId": "022bb90c-bbac-11e4-8dfc-aa07a5b093db",
    "receivedAt": "2015-02-23T22:28:55.387Z",
    "sentAt": "2015-02-23T22:28:55.111Z",
    "timestamp": "2015-02-23T22:28:55.111Z",
    "traits": {
      "name": "Peter Gibbons",
      "email": "peter@example.com",
      "plan": "premium",
      "logins": 5,
      "address": {
        "street": "6th St",
        "city": "San Francisco",
        "state": "CA",
        "postalCode": "94103",
        "country": "USA"
      }
    },
    "type": "identify",
    "userId": "97980cfea0067",
    "version": "1.1"
  }

const src = {
    "id": "sh-fc25464e-65E8-43B0-563A-24EA356C520D",
    "name": "checkout_contact_info_submitted",
    "data": {
        "checkout": {
            "attributes": [],
            "billingAddress": {
                "country": "IN",
                "countryCode": "IN",
                "province": "TS",
                "provinceCode": "TS"
            },
            "token": "dd84dba9362eab31f3513ebd3bd82b6c",
            "currencyCode": "INR",
            "discountApplications": [],
            "email": "",
            "phone": "",
            "lineItems": [
                {
                    "discountAllocations": [],
                    "id": "44843038015702",
                    "quantity": 1,
                    "title": "The Collection Snowboard: Liquid",
                    "variant": {
                        "id": "44843038015702",
                        "image": {
                            "src": "https://cdn.shopify.com/s/files/1/0688/7561/6470/products/Main_b13ad453-477c-4ed1-9b43-81f3345adfd6_64x64.jpg?v=1704619785"
                        },
                        "price": {
                            "amount": 749.95,
                            "currencyCode": "INR"
                        },
                        "product": {
                            "id": "8273464099030",
                            "title": "The Collection Snowboard: Liquid",
                            "vendor": "Hydrogen Vendor",
                            "type": "",
                            "untranslatedTitle": "The Collection Snowboard: Liquid",
                            "url": "/products/the-collection-snowboard-liquid"
                        }
                    }
                }
            ],
            "order": {},
            "shippingAddress": {
                "country": "IN",
                "countryCode": "IN"
            },
            "subtotalPrice": {
                "amount": 749.95,
                "currencyCode": "INR"
            },
            "shippingLine": {
                "price": {}
            },
            "totalTax": {
                "amount": 67.5,
                "currencyCode": "INR"
            },
            "totalPrice": {
                "amount": 817.45,
                "currencyCode": "INR"
            },
            "transactions": []
        }
    },
    "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
    "timestamp": "2024-01-12T05:29:08.639Z",
    "context": {
        "document": {
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5",
                "port": "",
                "protocol": "https:",
                "search": ""
            },
            "referrer": "https://quickstart-6ebc0909.myshopify.com/",
            "characterSet": "UTF-8",
            "title": "Checkout - Quickstart (6ebc0909)"
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
            "innerWidth": 584,
            "outerHeight": 775,
            "outerWidth": 1235,
            "pageXOffset": 0,
            "pageYOffset": 0,
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5",
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
}; */