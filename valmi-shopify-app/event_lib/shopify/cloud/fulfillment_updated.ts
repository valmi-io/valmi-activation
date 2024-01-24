/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 2:54:06 pm
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

export const mapping = (analytics_state: any): any => {
  return [   
    { "$.order_id": { to: "$.order_id" } }, 
    { "$.tracking_company": { to: "$.tracking_company" } }, 
    { "$.tracking_urls": { to: "$.tracking_urls" } }, 
    { "$.tracking_numbers": { to: "$.tracking_numbers" } }, 

    { "$.line_items[*].quantity": { to: "$.products[*].quantity" } },
    { "$.line_items[*].sku": { to: "$.products[*].sku" } },
    { "$.line_items[*].fulfillable_quantity": { to: "$.products[*].fulfillable_quantity" } },
    { "$.line_items[*].title": { to: "$.products[*].name" } },
    { "$.line_items[*].price": { to: "$.products[*].price" } },
    { "$.line_items[*].product_id": { to: "$.products[*].product_id" } },
    { "$.line_items[*].vendor": { to: "$.products[*].brand" } },
    { "$.line_items[*].fulfillment_status": { to: "$.products[*].fulfillment_status" } },
    { "$.line_items[*].fulfillment_service": { to: "$.products[*].fulfillment_service" } },
  ];
};
export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  return [{
    fn: valmiAnalytics.track.bind(null, "Fulfillment Updated - s2s"),
    mapping: mapping.bind(null, analytics_state),
    data: event,
  }]
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
const src = {
    "value": {
      "id": 4829441392854,
      "order_id": 5361240244438,
      "status": "success",
      "created_at": "2024-01-12T04:23:27-05:00",
      "service": "gift_card",
      "updated_at": "2024-01-12T04:23:27-05:00",
      "tracking_company": null,
      "shipment_status": null,
      "location_id": 73971466454,
      "origin_address": null,
      "email": "raj@mw.com",
      "destination": null,
      "line_items": [
        {
          "id": 13340254503126,
          "variant_id": 44843037688022,
          "title": "GiftCard",
          "quantity": 1,
          "sku": "",
          "variant_title": "$10",
          "vendor": "SnowboardVendor",
          "fulfillment_service": "gift_card",
          "product_id": 8273463836886,
          "requires_shipping": false,
          "taxable": false,
          "gift_card": true,
          "name": "GiftCard-$10",
          "variant_inventory_management": null,
          "properties": [],
          "product_exists": true,
          "fulfillable_quantity": 0,
          "grams": 0,
          "price": "10.00",
          "total_discount": "0.00",
          "fulfillment_status": "fulfilled",
          "price_set": {
            "shop_money": {
              "amount": "10.00",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "10.00",
              "currency_code": "INR"
            }
          },
          "total_discount_set": {
            "shop_money": {
              "amount": "0.00",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "0.00",
              "currency_code": "INR"
            }
          },
          "discount_allocations": [],
          "duties": [],
          "admin_graphql_api_id": "gid://shopify/LineItem/13340254503126",
          "tax_lines": []
        }
      ],
      "tracking_number": null,
      "tracking_numbers": [],
      "tracking_url": null,
      "tracking_urls": [],
      "receipt": {
        "gift_cards": [
          {
            "id": 544934756566,
            "line_item_id": 13340254503126,
            "masked_code": "••••••••••••ghg2"
          }
        ]
      },
      "name": "#1003.1",
      "admin_graphql_api_id": "gid://shopify/Fulfillment/4829441392854"
    },
    "space": 2
  };


  //partial fulfillment
  const src1 = {
    "value": {
      "id": 4829430743254,
      "order_id": 5361237360854,
      "status": "cancelled",
      "created_at": "2024-01-12T03:51:44-05:00",
      "service": "manual",
      "updated_at": "2024-01-12T04:32:03-05:00",
      "tracking_company": "Other",
      "shipment_status": null,
      "location_id": 73971466454,
      "origin_address": null,
      "email": "raj@mywavia.com",
      "destination": {
        "first_name": "Swathi",
        "address1": "210,Lakshmimegatownship,ragannaguda",
        "phone": null,
        "city": "Hyderabad",
        "zip": "501510",
        "province": "Telangana",
        "country": "India",
        "last_name": "Varkala",
        "address2": null,
        "company": null,
        "latitude": 17.2629066,
        "longitude": 78.5860155,
        "name": "SwathiVarkala",
        "country_code": "IN",
        "province_code": "TS"
      },
      "line_items": [
        {
          "id": 13340248965334,
          "variant_id": 44843038015702,
          "title": "TheCollectionSnowboard:Liquid",
          "quantity": 4,
          "sku": "",
          "variant_title": null,
          "vendor": "HydrogenVendor",
          "fulfillment_service": "manual",
          "product_id": 8273464099030,
          "requires_shipping": true,
          "taxable": true,
          "gift_card": false,
          "name": "TheCollectionSnowboard:Liquid",
          "variant_inventory_management": "shopify",
          "properties": [],
          "product_exists": true,
          "fulfillable_quantity": 1,
          "grams": 0,
          "price": "749.95",
          "total_discount": "0.00",
          "fulfillment_status": "partial",
          "price_set": {
            "shop_money": {
              "amount": "749.95",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "749.95",
              "currency_code": "INR"
            }
          },
          "total_discount_set": {
            "shop_money": {
              "amount": "0.00",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "0.00",
              "currency_code": "INR"
            }
          },
          "discount_allocations": [],
          "duties": [],
          "admin_graphql_api_id": "gid://shopify/LineItem/13340248965334",
          "tax_lines": [
            {
              "title": "IGST",
              "price": "539.97",
              "rate": 0.18,
              "channel_liable": false,
              "price_set": {
                "shop_money": {
                  "amount": "539.97",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "539.97",
                  "currency_code": "INR"
                }
              }
            }
          ]
        },
        {
          "id": 13340248998102,
          "variant_id": 44843037917398,
          "title": "TheMulti-managedSnowboard",
          "quantity": 1,
          "sku": "sku-managed-1",
          "variant_title": null,
          "vendor": "Multi-managedVendor",
          "fulfillment_service": "manual",
          "product_id": 8273463967958,
          "requires_shipping": true,
          "taxable": true,
          "gift_card": false,
          "name": "TheMulti-managedSnowboard",
          "variant_inventory_management": "shopify",
          "properties": [],
          "product_exists": true,
          "fulfillable_quantity": 1,
          "grams": 0,
          "price": "629.95",
          "total_discount": "0.00",
          "fulfillment_status": null,
          "price_set": {
            "shop_money": {
              "amount": "629.95",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "629.95",
              "currency_code": "INR"
            }
          },
          "total_discount_set": {
            "shop_money": {
              "amount": "0.00",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "0.00",
              "currency_code": "INR"
            }
          },
          "discount_allocations": [],
          "duties": [],
          "admin_graphql_api_id": "gid://shopify/LineItem/13340248998102",
          "tax_lines": [
            {
              "title": "IGST",
              "price": "113.39",
              "rate": 0.18,
              "channel_liable": false,
              "price_set": {
                "shop_money": {
                  "amount": "113.39",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "113.39",
                  "currency_code": "INR"
                }
              }
            }
          ]
        }
      ],
      "tracking_number": "1",
      "tracking_numbers": [
        "1"
      ],
      "tracking_url": null,
      "tracking_urls": [],
      "receipt": {},
      "name": "#1001.1",
      "admin_graphql_api_id": "gid://shopify/Fulfillment/4829430743254"
    },
    "space": 2
  };*/