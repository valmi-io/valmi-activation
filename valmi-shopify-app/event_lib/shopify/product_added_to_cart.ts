/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";
 
export const mapping = (): any => {
  return [  
    { "$.data.cartLine.merchandise.price.currencyCode": { to: "$.currency" } },
    { "$.data.cartLine.merchandise.price.amount": { to: "$.price" } },
    { "$.data.cartLine.merchandise.image.src": { to: "$.image_url" } },
    { "$.data.cartLine.merchandise.product.url": { to: "$.url" } },
    { "$.data.cartLine.merchandise.product.title": { to: "$.name" } },
    { "$.data.cartLine.merchandise.sku": { to: "$.sku" } },
    { "$.data.cartLine.merchandise.product.id": { to: "$.product_id" } },
    { "$.data.cartLine.merchandise.product.type": { to: "$.category" } },
    { "$.data.cartLine.merchandise.product.vendor": { to: "$.brand" } },
    { "$.data.cartLine.cost.totalAmount.amount": { to: "$.value" } },
    { "$.data.cartLine.quantity": { to: "$.quantity" } },

  ];
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
const src = {
    "id": "sh-fc065e5e-ED1B-4377-D2D5-2921947B586D",
    "name": "product_added_to_cart",
    "data": {
        "cartLine": {
            "cost": {
                "totalAmount": {
                    "amount": 749.95,
                    "currencyCode": "INR"
                }
            },
            "merchandise": {
                "id": "44843038015702",
                "image": {
                    "src": "https://cdn.shopify.com/s/files/1/0688/7561/6470/products/Main_b13ad453-477c-4ed1-9b43-81f3345adfd6.jpg?v=1704619785"
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
                    "url": "/products/the-collection-snowboard-liquid?variant=44843038015702"
                },
                "sku": "",
                "title": null,
                "untranslatedTitle": null
            },
            "quantity": 1
        }
    },
    "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
    "timestamp": "2024-01-12T04:54:15.677Z",
    "context": {
        "document": {
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/products/the-collection-snowboard-liquid?pr_prod_strat=collection_fallback&pr_rec_id=66be974f6&pr_rec_pid=8273464099030&pr_ref_pid=8273464000726&pr_seq=uniform",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/products/the-collection-snowboard-liquid",
                "port": "",
                "protocol": "https:",
                "search": "?pr_prod_strat=collection_fallback&pr_rec_id=66be974f6&pr_rec_pid=8273464099030&pr_ref_pid=8273464000726&pr_seq=uniform"
            },
            "referrer": "https://quickstart-6ebc0909.myshopify.com/products/the-multi-location-snowboard",
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
            "innerWidth": 584,
            "outerHeight": 775,
            "outerWidth": 1235,
            "pageXOffset": 0,
            "pageYOffset": 0,
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/products/the-collection-snowboard-liquid?pr_prod_strat=collection_fallback&pr_rec_id=66be974f6&pr_rec_pid=8273464099030&pr_ref_pid=8273464000726&pr_seq=uniform",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/products/the-collection-snowboard-liquid",
                "port": "",
                "protocol": "https:",
                "search": "?pr_prod_strat=collection_fallback&pr_rec_id=66be974f6&pr_rec_pid=8273464099030&pr_ref_pid=8273464000726&pr_seq=uniform"
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