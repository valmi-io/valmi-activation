/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 10:21:47 am
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

export const mapping = (): any => {
  return [
    //   "$.context.document.location.search": {to: "$.brand"},
    //   "$.context.document.location.search": {to: "$.variant"},
    //   "$.context.document.location.search": {to: "$.quantity"},
    //   "$.context.document.location.search": {to: "$.coupon"},
    //   "$.context.document.location.search": {to: "$.position"},
    //   "$.context.document.location.search": {to: "$.value"},

    { "$.data.productVariant.price.currencyCode": { to: "$.currency" } },
    { "$.data.productVariant.price.amount": { to: "$.price" } },
    { "$.data.productVariant.image.src": { to: "$.image_url" } },
    { "$.data.productVariant.product.url": { to: "$.url" } },
    { "$.data.productVariant.product.title": { to: "$.name" } },
    { "$.data.productVariant.product.sku": { to: "$.sku" } },
    { "$.data.productVariant.product.id": { to: "$.product_id" } },
    { "$.data.productVariant.product.type": { to: "$.category" } },
    { "$.data.productVariant.product.vendor": { to: "$.brand" } },
    { "$.data.productVariant.price.amount": { to: "$.value" } },
  ];
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;


/*
analytics.track('Product Viewed', {
    product_id: '507f1f77bcf86cd799439011',
    sku: 'G-32',
    category: 'Games',
    name: 'Monopoly: 3rd Edition',
    brand: 'Hasbro',
    variant: '200 pieces',
    price: 18.99,
    quantity: 1,
    coupon: 'MAYDEALS',
    currency: 'usd',
    position: 3,
    value: 18.99,
    url: 'https://www.example.com/product/path',
    image_url: 'https://www.example.com/product/path.jpg'
  });

const src = {
    "id": "sh-fc02d5d7-B147-4D38-659D-BCF75AE8DB75",
    "name": "product_viewed",
    "data": {
        "productVariant": {
            "id": "44843037950166",
            "image": {
                "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_0a4e9096-021a-4c1e-8750-24b233166a12.jpg?v=1704619783"
            },
            "price": {
                "amount": 729.95,
                "currencyCode": "INR"
            },
            "product": {
                "id": "8273464000726",
                "title": "The Multi-location Snowboard",
                "untranslatedTitle": "The Multi-location Snowboard",
                "url": "/products/the-multi-location-snowboard",
                "vendor": "Quickstart (6ebc0909)",
                "type": ""
            },
            "sku": "",
            "title": "Default Title",
            "untranslatedTitle": "Default Title"
        }
    },
    "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
    "timestamp": "2024-01-12T04:51:32.647Z",
    "context": {
        "document": {
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/products/the-multi-location-snowboard",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/products/the-multi-location-snowboard",
                "port": "",
                "protocol": "https:",
                "search": ""
            },
            "referrer": "https://quickstart-6ebc0909.myshopify.com/",
            "characterSet": "UTF-8",
            "title": "The Multi-location Snowboard – Quickstart (6ebc0909)"
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
                "href": "https://quickstart-6ebc0909.myshopify.com/products/the-multi-location-snowboard",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/products/the-multi-location-snowboard",
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
*/