/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = (): any => {
  return [ 
    { "$.data.collection.id": { to: "$.list_id" } },  
    { "$.data.collection.title": { to: "$.category" } },  
    { "$.data.collection.productVariants[*].price.currencyCode": { to: "$.products[*].currency" } },
    { "$.data.collection.productVariants[*].price.amount": { to: "$.products[*].price" } },
    { "$.data.collection.productVariants[*].image.src": { to: "$.products[*].image_url" } },
    { "$.data.collection.productVariants[*].product.url": { to: "$.products[*].url" } },
    { "$.data.collection.productVariants[*].product.title": { to: "$.products[*].name" } },
    { "$.data.collection.productVariants[*].product.sku": { to: "$.products[*].sku" } },
    { "$.data.collection.productVariants[*].product.id": { to: "$.products[*].product_id" } },
    { "$.data.collection.productVariants[*].product.type": { to: "$.products[*].category" } },
    { "$.data.collection.productVariants[*].product.vendor": { to: "$.products[*].brand" } },
    { "$.data.collection.productVariants[*].price.amount": { to: "$.products[*].value" } },
  ];
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;



/*
analytics.track('Product List Viewed', {
    list_id: 'hot_deals_1',
    category: 'Deals',
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
const src= {
    "id": "sh-fbfe9701-EDCA-4E62-5EAA-4B0AEFFC08DC",
    "name": "collection_viewed",
    "data": {
        "collection": {
            "id": "",
            "title": "Products",
            "productVariants": [
                {
                    "id": "44843037688022",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/gift_card.png?v=1704619782"
                    },
                    "price": {
                        "amount": 10,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463836886",
                        "title": "Gift Card",
                        "untranslatedTitle": "Gift Card",
                        "url": "/products/gift-card",
                        "vendor": "Snowboard Vendor",
                        "type": ""
                    },
                    "sku": "",
                    "title": "$10",
                    "untranslatedTitle": "$10"
                },
                {
                    "id": "44843038048470",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/snowboard_wax.png?v=1704619785"
                    },
                    "price": {
                        "amount": 24.95,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273464066262",
                        "title": "Selling Plans Ski Wax",
                        "untranslatedTitle": "Selling Plans Ski Wax",
                        "url": "/products/selling-plans-ski-wax",
                        "vendor": "Quickstart (6ebc0909)",
                        "type": ""
                    },
                    "sku": "",
                    "title": "Selling Plans Ski Wax",
                    "untranslatedTitle": "Selling Plans Ski Wax"
                },
                {
                    "id": "44843037884630",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_b9e0da7f-db89-4d41-83f0-7f417b02831d.jpg?v=1704619782"
                    },
                    "price": {
                        "amount": 2629.95,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463935190",
                        "title": "The 3p Fulfilled Snowboard",
                        "untranslatedTitle": "The 3p Fulfilled Snowboard",
                        "url": "/products/the-3p-fulfilled-snowboard",
                        "vendor": "Quickstart (6ebc0909)",
                        "type": ""
                    },
                    "sku": "sku-hosted-1",
                    "title": "Default Title",
                    "untranslatedTitle": "Default Title"
                },
                {
                    "id": "44843037589718",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_0a40b01b-5021-48c1-80d1-aa8ab4876d3d.jpg?v=1704619782"
                    },
                    "price": {
                        "amount": 600,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463738582",
                        "title": "The Collection Snowboard: Hydrogen",
                        "untranslatedTitle": "The Collection Snowboard: Hydrogen",
                        "url": "/products/the-collection-snowboard-hydrogen",
                        "vendor": "Hydrogen Vendor",
                        "type": ""
                    },
                    "sku": "",
                    "title": "Default Title",
                    "untranslatedTitle": "Default Title"
                },
                {
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
                {
                    "id": "44843037982934",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_d624f226-0a89-4fe1-b333-0d1548b43c06.jpg?v=1704619783"
                    },
                    "price": {
                        "amount": 1025,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273464033494",
                        "title": "The Collection Snowboard: Oxygen",
                        "untranslatedTitle": "The Collection Snowboard: Oxygen",
                        "url": "/products/the-collection-snowboard-oxygen",
                        "vendor": "Hydrogen Vendor",
                        "type": ""
                    },
                    "sku": "",
                    "title": "Default Title",
                    "untranslatedTitle": "Default Title"
                },
                {
                    "id": "44843037851862",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/snowboard_sky.png?v=1704619782"
                    },
                    "price": {
                        "amount": 785.95,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463902422",
                        "title": "The Compare at Price Snowboard",
                        "untranslatedTitle": "The Compare at Price Snowboard",
                        "url": "/products/the-compare-at-price-snowboard",
                        "vendor": "Quickstart (6ebc0909)",
                        "type": ""
                    },
                    "sku": "",
                    "title": "Default Title",
                    "untranslatedTitle": "Default Title"
                },
                {
                    "id": "44843037425878",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_589fc064-24a2-4236-9eaf-13b2bd35d21d.jpg?v=1704619782"
                    },
                    "price": {
                        "amount": 699.95,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463673046",
                        "title": "The Complete Snowboard",
                        "untranslatedTitle": "The Complete Snowboard",
                        "url": "/products/the-complete-snowboard",
                        "vendor": "Snowboard Vendor",
                        "type": "snowboard"
                    },
                    "sku": "",
                    "title": "Ice",
                    "untranslatedTitle": "Ice"
                },
                {
                    "id": "44843037819094",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/snowboard_purple_hydrogen.png?v=1704619782"
                    },
                    "price": {
                        "amount": 949.95,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463869654",
                        "title": "The Inventory Not Tracked Snowboard",
                        "untranslatedTitle": "The Inventory Not Tracked Snowboard",
                        "url": "/products/the-inventory-not-tracked-snowboard",
                        "vendor": "Quickstart (6ebc0909)",
                        "type": ""
                    },
                    "sku": "sku-untracked-1",
                    "title": "Default Title",
                    "untranslatedTitle": "Default Title"
                },
                {
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
                },
                {
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
                {
                    "id": "44843037655254",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/products/Main_f44a9605-cd62-464d-b095-d45cdaa0d0d7.jpg?v=1704619782"
                    },
                    "price": {
                        "amount": 885.95,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463804118",
                        "title": "The Out of Stock Snowboard",
                        "untranslatedTitle": "The Out of Stock Snowboard",
                        "url": "/products/the-out-of-stock-snowboard",
                        "vendor": "Quickstart (6ebc0909)",
                        "type": ""
                    },
                    "sku": "",
                    "title": "Default Title",
                    "untranslatedTitle": "Default Title"
                },
                {
                    "id": "44843037327574",
                    "image": {
                        "src": "//quickstart-6ebc0909.myshopify.com/cdn/shop/files/Main.jpg?v=1704619782"
                    },
                    "price": {
                        "amount": 885.95,
                        "currencyCode": "INR"
                    },
                    "product": {
                        "id": "8273463574742",
                        "title": "The Videographer Snowboard",
                        "untranslatedTitle": "The Videographer Snowboard",
                        "url": "/products/the-videographer-snowboard",
                        "vendor": "Quickstart (6ebc0909)",
                        "type": ""
                    },
                    "sku": "",
                    "title": "Default Title",
                    "untranslatedTitle": "Default Title"
                }
            ]
        }
    },
    "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
    "timestamp": "2024-01-12T04:46:54.394Z",
    "context": {
        "document": {
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/collections/all",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/collections/all",
                "port": "",
                "protocol": "https:",
                "search": ""
            },
            "referrer": "https://quickstart-6ebc0909.myshopify.com/",
            "characterSet": "UTF-8",
            "title": "Products – Quickstart (6ebc0909)"
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
                "href": "https://quickstart-6ebc0909.myshopify.com/collections/all",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/collections/all",
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