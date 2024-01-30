/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = (): any => {
  return [ 
    { "$.data.cart.id": { to: "$.cart_id" } },  
    { "$.data.cart.cost.totalAmount.amount": { to: "$.value" }},  
    { "$.data.cart.cost.totalAmount.currencyCode": { to: "$.currency" }},  
    { "$.data.cart.totalQuantity": { to: "$.quantity" }},  

    { "$.data.cart.lines[*].merchandise.price.currencyCode": { to: "$.products[*].currency" } },
    { "$.data.cart.lines[*].merchandise.price.amount": { to: "$.products[*].price" } },
    { "$.data.cart.lines[*].merchandise.image.src": { to: "$.products[*].image_url" } },
    { "$.data.cart.lines[*].merchandise.product.url": { to: "$.products[*].url" } },
    { "$.data.cart.lines[*].merchandise.product.title": { to: "$.products[*].name" } },
    { "$.data.cart.lines[*].merchandise.product.sku": { to: "$.products[*].sku" } },
    { "$.data.cart.lines[*].merchandise.product.id": { to: "$.products[*].product_id" } },
    { "$.data.cart.lines[*].merchandise.product.type": { to: "$.products[*].category" } },
    { "$.data.cart.lines[*].merchandise.product.vendor": { to: "$.products[*].brand" } },
    { "$.data.cart.lines[*].cost.totalAmount.amount": { to: "$.products[*].value" } },
    { "$.data.cart.lines[*].quantity": { to: "$.products[*].quantity" } },

  ];
};
export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;


/*

analytics.track('Cart Viewed', {
    cart_id: 'd92jd29jd92jd29j92d92jd',
    products: [
      {
        product_id: '507f1f77bcf86cd799439011',
        sku: '45790-32',
        name: 'Monopoly: 3rd Edition',
        price: 19,
        position: 1,
        category: 'Games',
        url: 'https://www.example.com/product/path',
        image_url: 'https://www.example.com/product/path.jpg'
      },
      {
        product_id: '505bd76785ebb509fc183733',
        sku: '46493-32',
        name: 'Uno Card Game',
        price: 3,
        position: 2,
        category: 'Games'
      }
    ]
  });

const src ={
    "id": "shu-0244002a-4FDB-4C98-457E-813359A5DDF6",
    "name": "cart_viewed",
    "data": {
        "cart": {
            "cost": {
                "totalAmount": {
                    "amount": 2009.85,
                    "currencyCode": "INR"
                }
            },
            "id": "Z2NwLXVzLWNlbnRyYWwxOjAxSEtZMllEN0NZTkEwRVo3QlpHMkUyMEo4",
            "lines": [
                {
                    "cost": {
                        "totalAmount": {
                            "amount": 1259.9,
                            "currencyCode": "INR"
                        }
                    },
                    "merchandise": {
                        "id": "44843037917398",
                        "image": {
                            "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_9129b69a-0c7b-4f66-b6cf-c4222f18028a.jpg?v=1704619782"
                        },
                        "price": {
                            "amount": 629.95,
                            "currencyCode": "INR"
                        },
                        "product": {
                            "id": "8273463967958",
                            "title": "The Multi-managed Snowboard",
                            "untranslatedTitle": "The Multi-managed Snowboard",
                            "url": "/products/the-multi-managed-snowboard",
                            "vendor": "Multi-managed Vendor",
                            "type": ""
                        },
                        "sku": "sku-managed-1",
                        "title": "Default Title",
                        "untranslatedTitle": "Default Title"
                    },
                    "quantity": 2
                },
                {
                    "cost": {
                        "totalAmount": {
                            "amount": 749.95,
                            "currencyCode": "INR"
                        }
                    },
                    "merchandise": {
                        "id": "44843038015702",
                        "image": {
                            "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_b13ad453-477c-4ed1-9b43-81f3345adfd6.jpg?v=1704619785"
                        },
                        "price": {
                            "amount": 749.95,
                            "currencyCode": "INR"
                        },
                        "product": {
                            "id": "8273464099030",
                            "title": "The Collection Snowboard: Liquid",
                            "untranslatedTitle": "The Collection Snowboard: Liquid",
                            "url": "/products/the-collection-snowboard-liquid",
                            "vendor": "Hydrogen Vendor",
                            "type": ""
                        },
                        "sku": "",
                        "title": "Default Title",
                        "untranslatedTitle": "Default Title"
                    },
                    "quantity": 1
                }
            ],
            "totalQuantity": 3
        }
    },
    "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
    "timestamp": "2024-01-13T10:00:26.571Z",
    "context": {
        "document": {
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/cart",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/cart",
                "port": "",
                "protocol": "https:",
                "search": ""
            },
            "referrer": "https://quickstart-6ebc0909.myshopify.com/",
            "characterSet": "UTF-8",
            "title": "Your Shopping Cart – Quickstart (6ebc0909)"
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
            "innerWidth": 728,
            "outerHeight": 775,
            "outerWidth": 1234,
            "pageXOffset": 0,
            "pageYOffset": 0,
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/cart",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/cart",
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