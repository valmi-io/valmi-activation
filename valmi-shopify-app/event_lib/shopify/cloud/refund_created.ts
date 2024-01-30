/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = (analytics_state: any): any => {
  return [  
    { "$.order_id": { to: "$.order_id" } }, 
    { "$.total_tax": { to: "$.tax" } },
    { "$.subtotal": { to: "$.revenue" } },
    { "$.total": { to: "$.value" } },
    { "$.currency": { to: "$.currency" } },
  

    { "$.refund_line_items[*].quantity": { to: "$.products[*].quantity" } },
    { "$.refund_line_items[*].line_item.sku": { to: "$.products[*].sku" } },
    { "$.refund_line_items[*].line_item.title": { to: "$.products[*].name" } },
    { "$.refund_line_items[*].line_item.price": { to: "$.products[*].price" } },
    { "$.refund_line_items[*].line_item.product_id": { to: "$.products[*].product_id" } },
    { "$.refund_line_items[*].line_item.vendor": { to: "$.products[*].brand" } },
  ];
};
export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  event.total_tax = 0;
  event.subtotal = 0
  event.total = 0;
  if(event.refund_line_items.length > 0){
    for(let i = 0; i < event.refund_line_items.length; i++){
      event.total_tax += event.refund_line_items[i].total_tax;
      event.subtotal += event.refund_line_items[i].subtotal;
      event.total = event.total_tax + event.subtotal;
    }
  }
  if(event.transactions.length >0){
    event.currency = event.transactions[0].currency;
  }
  return [{
    fn: valmiAnalytics.track.bind(null, "Order Refunded - s2s"),
    mapping: mapping.bind(null, analytics_state),
    data: event,
  }]
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
//without return
const src = {
    id: 887837196502,
    order_id: 5364772372694,
    created_at: '2024-01-12T03:48:28-05:00',
    note: 'x',
    user_id: 89705382102,
    processed_at: '2024-01-12T03:48:28-05:00',
    restock: true,
    duties: [],
    total_duties_set: {
      shop_money: { amount: '0.00', currency_code: 'INR' },
      presentment_money: { amount: '0.00', currency_code: 'INR' }
    },
    return: null,
    admin_graphql_api_id: 'gid://shopify/Refund/887837196502',
    refund_line_items: [
      {
        id: 450826502358,
        quantity: 2,
        line_item_id: 13347497050326,
        location_id: 73971466454,
        restock_type: 'cancel',
        subtotal: 1259.9,
        total_tax: 226.78,
        subtotal_set: [Object],
        total_tax_set: [Object],
        line_item: [Object]
      },
      {
        id: 450826535126,
        quantity: 2,
        line_item_id: 13347497083094,
        location_id: 73971466454,
        restock_type: 'cancel',
        subtotal: 1499.9,
        total_tax: 269.98,
        subtotal_set: [Object],
        total_tax_set: [Object],
        line_item: [Object]
      }
    ],
    transactions: [
      {
        id: 6327309467862,
        order_id: 5364772372694,
        kind: 'refund',
        gateway: 'bogus',
        status: 'success',
        message: 'Bogus Gateway: Forced success',
        created_at: '2024-01-12T03:48:27-05:00',
        test: true,
        authorization: null,
        location_id: null,
        user_id: 89705382102,
        parent_id: 6327269261526,
        processed_at: '2024-01-12T03:48:27-05:00',
        device_id: null,
        error_code: null,
        source_name: '1830279',
        payment_details: [Object],
        receipt: [Object],
        amount: '3256.56',
        currency: 'INR',
        payment_id: '#1005.2',
        total_unsettled_set: [Object],
        manual_payment_gateway: false,
        admin_graphql_api_id: 'gid://shopify/OrderTransaction/6327309467862'
      }
    ],
    order_adjustments: []
  };

  //with return
  const src1 = {
    id: 887837262038,
    order_id: 5364786725078,
    created_at: '2024-01-12T03:49:48-05:00',
    note: null,
    user_id: 89705382102,
    processed_at: '2024-01-12T03:49:48-05:00',
    restock: true,
    duties: [],
    total_duties_set: {
      shop_money: { amount: '0.00', currency_code: 'INR' },
      presentment_money: { amount: '0.00', currency_code: 'INR' }
    },
    return: {
      id: 5966627030,
      admin_graphql_api_id: 'gid://shopify/Return/5966627030'
    },
    admin_graphql_api_id: 'gid://shopify/Refund/887837262038',
    refund_line_items: [
      {
        id: 450826567894,
        quantity: 1,
        line_item_id: 13347521822934,
        location_id: 73971466454,
        restock_type: 'return',
        subtotal: 749.95,
        total_tax: 134.99,
        subtotal_set: [Object],
        total_tax_set: [Object],
        line_item: [Object]
      }
    ],
    transactions: [
      {
        id: 6327310254294,
        order_id: 5364786725078,
        kind: 'refund',
        gateway: 'bogus',
        status: 'success',
        message: 'Bogus Gateway: Forced success',
        created_at: '2024-01-12T03:49:48-05:00',
        test: true,
        authorization: null,
        location_id: null,
        user_id: 89705382102,
        parent_id: 6327288234198,
        processed_at: '2024-01-12T03:49:48-05:00',
        device_id: null,
        error_code: null,
        source_name: '1830279',
        payment_details: [Object],
        receipt: [Object],
        amount: '884.94',
        currency: 'INR',
        payment_id: '#1006.2',
        total_unsettled_set: [Object],
        manual_payment_gateway: false,
        admin_graphql_api_id: 'gid://shopify/OrderTransaction/6327310254294'
      }
    ],
    order_adjustments: []
  };
  const src3 = { 
      "id": 887838376150,
      "order_id": 5361237360854,
      "created_at": "2024-01-12T04:10:23-05:00",
      "note": null,
      "user_id  ": 89705382102,
      "processed_at": "2024-01-12T04:10:23-05:00",
      "restock": true,
      "duties": [],
      "total_duties_set": {
        "shop_money": {
          "amount": "0.00",
          "currency_code": "IN  R"
        },
        "presentment_money": {
          "amount": "0.00",
          "currency_code": "INR"
        }
      },
      "return": {
        "id": 5966856406,
        "admin_graphql_api_id": "gid://shopify/Return/5966856406"
      },
      "adm  in_graphql_api_id": "gid://shopify/Refund/887838376150",
      "refund_line_items": [
        {
          "id": 450827518166,
          "quantity": 1,
          "line_item_id": 13340248965334,
          "location_id": 73971466454,
          "restock_type": "return",
          "subtotal": 749.95,
          "total_tax": 134.99,
          "subtotal_set": {
            "shop_money": {
              "amount": "749.95",
              "currency_code": "INR"
            },
            "presentme  nt_money": {
              "amount": "749.95",
              "currency_code": "INR"
            }
          },
          "total_tax_set": {
            "shop_money": {
              "amount": "134.99",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount  ": "134.99",
              "currency_code": "INR"
            }
          },
          "line_item": {
            "id": 13340248965334,
            "variant_id": 44843038015702,
            "title": "The Collection Snowboard:   Liquid",
            "quantity": 4,
            "sku": "",
            "variant_title": null,
            "vendor": "Hydrogen   Vendor",
            "fulfillment_service": "manual",
            "product_id": 8273464099030,
            "requires_shipping": true,
            "taxable": true,
            "gift_card": false,
            "name": "The Collection   Snowboard:   Liquid",
            "variant_inventory_management": "shopify",
            "properties": [],
            "product_exists": true,
            "fulfillable_quantity": 0,
            "grams": 0,
            "price": "749.95",
            "total_discoun  t": "0.00",
            "fulfillment_status": "fulfilled",
            "price_set": {
              "shop_money": {
                "amount": "749.95",
                "currency_code": "INR"
              },
              "presentment_money": {
                "amount": "749.95",
                "cu  rrency_code": "INR"
              }
            },
            "total_discount_set": {
              "shop_money": {
                "amount": "0.00",
                "currency_code": "INR"
              },
              "presentment_money": {
                "amount": "0.00",
                "currency_code": "INR  "
              }
            },
            "discount_allocations": [],
            "duties": [],
            "admin_graphql_api_id": "gid://shopify/LineItem/13340248965334",
            "tax_lines": [
              {
                "title": "IGST",
                "price": "539.97",
                "r  ate": 0.18,
                "channel_liable": false,
                "price_set": {
                  "shop_money": {
                    "amount": "539.97",
                    "currency_code": "INR"
                  },
                  "presentment_money": {
                    "amount": "539.97",
                    "currency_cod  e": "INR"
                  }
                }
              }
            ]
          }
        }
      ],
      "transactions": [
        {
          "id": 6327321133270,
          "order_id": 5361237360854,
          "kind": "refund",
          "gateway": "bogus",
          "status": "success",
          "message": "Bogus   Gateway: Forced success",
          "created_at": "2024-01-12T04:10:22-05:00",
          "test": true,
          "authorization": null,
          "location_id": null,
          "user_id": 89705382102,
          "parent_id": 6322113806550,
          "processed_at": "2024-01-12T04:10:22-05:00",
          "device_id": null,
          "error_code": null,
          "source_name": "1830279",
          "payment_details": {
            "credit_card_bin": "  1",
            "avs_result_code": null,
            "cvv_result_code": null,
            "credit_card_number": "•••• •••• ••••   1",
            "credit_card_company": "Bogus",
            "buyer_action_info": null,
            "credit_card_name": "VARKALA RAJASHEKAR",
            "credit_card_wallet": null,
            "credit_card_expiration_month  ": 10,
            "credit_card_expiration_year": 2024,
            "payment_method_name": "bogus"
          },
          "receipt": {
            "paid_amount": "884.94"
          },
          "amount": "884.94",
          "currency": "INR",
          "payment_id": "#1001.4",
          "total_unsettled_set": {
            "presentment_money": {
              "amount": "0.0",
              "currency": "INR"
            },
            "shop_money": {
              "amount": "0.0",
              "currency": "INR"
            }
          },
          "manual_payment_g  ateway": false,
          "admin_graphql_api_id": "gid://shopify/OrderTransaction/6327321133270"
        }
      ],
      "order_adjustments": []
    };*/