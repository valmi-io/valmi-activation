/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = (): any => {
  return [ 
    { "$.data.checkout.token": { to: "$.checkout_id" } },

    { "$.data.checkout.currencyCode": { to: "$.currency" } },
    { "$.data.checkout.totalTax": { to: "$.tax" } },
    { "$.data.checkout.discountApplications": { to: "$.discountApplications" } },
    { "$.data.checkout.subtotalPrice": { to: "$.revenue" } },
    { "$.data.checkout.totalPrice": { to: "$.value" } },
    
    { "$.data.checkout.billingAddress": { to: "$.billing_address" } },
    { "$.data.checkout.shippingAddress": { to: "$.shipping_address" } },
    
    { "$.data.checkout.lineItems[*].variant.price.amount": { to: "$.products[*].price" } },
    { "$.data.checkout.lineItems[*].variant.image.src": { to: "$.products[*].image_url" } },
    { "$.data.checkout.lineItems[*].variant.product.url": { to: "$.products[*].url" } },
    { "$.data.checkout.lineItems[*].variant.product.title": { to: "$.products[*].name" } },
    { "$.data.checkout.lineItems[*].variant.product.id": { to: "$.products[*].product_id" } },
    { "$.data.checkout.lineItems[*].variant.product.type": { to: "$.products[*].category" } },
    { "$.data.checkout.lineItems[*].variant.product.vendor": { to: "$.products[*].brand" } },
    { "$.data.checkout.lineItems[*].quantity": { to: "$.products[*].quantity" } },

    
  ];
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
const src = {
    "id": "sh-fc25464d-85AC-4A1C-CF92-DC0BFE51CA69",
    "name": "checkout_started",
    "data": {
        "checkout": {
            "attributes": [],
            "billingAddress": {},
            "token": "dd84dba9362eab31f3513ebd3bd82b6c",
            "currencyCode": "INR",
            "discountApplications": [],
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
            "shippingAddress": {},
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
    "timestamp": "2024-01-12T05:29:08.638Z",
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
};*/