/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = (analytics_state: any): any => {
  return [  
    { "$.cart_token": { to: "$.cart_id" } },
    { "$.checkout_token": { to: "$.checkout_id" } },
    { "$.id": { to: "$.order_id" } }, 
    { "$.total_tax": { to: "$.tax" } },
    { "$.currency": { to: "$.currency" } },
    { "$.total_discounts": { to: "$.discount" } },
    { "$.subtotal_price": { to: "$.revenue" } },
    { "$.total_price": { to: "$.value" } },
    { "$.discount_codes": { to: "$.coupon" } },
    
    { "$.line_items[*].quantity": { to: "$.products[*].quantity" } },
    { "$.line_items[*].sku": { to: "$.products[*].sku" } },
    { "$.line_items[*].title": { to: "$.products[*].name" } },
    { "$.line_items[*].price": { to: "$.products[*].price" } },
    { "$.line_items[*].product_id": { to: "$.products[*].product_id" } },
    { "$.line_items[*].vendor": { to: "$.products[*].brand" } },
  ];
};
export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  return [{
    fn: valmiAnalytics.track.bind(null, "Order Cancelled - s2s"),
    mapping: mapping.bind(null, analytics_state),
    data: event,
  }]
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*

const src = { 
      "id": 5364772372694,
      "admin_graphql_api_id": "gid://shopify/Order/5364772372694",
      "app_id": 580111,
      "browser_ip": "49.43.230.128",
      "buyer_accepts_marketing": false,
      "cancel_reason": "customer",
      "cancelled_at": "2024-01-12T04:36:00-05:00",
      "cart_token": "Z2NwLXVzLWNlbnRyYWwxOjAxSEtZOUJXMDdHVldNNjBSWlZZVkUxQ1o3",
      "checkout_id": 34309611520214,
      "checkout_token": "f25117962ca5a0f0f78896f36ca232a2",
      "client_details": {
        "accept_language": "en-IN",
        "browser_height": null,
        "browser_ip": "49.43.230.128",
        "browser_width": null,
        "session_hash": null,
        "user_agent": "Mozilla/5.0(Macintosh;IntelMacOSX10_15_7)AppleWebKit/537.36(KHTML,likeGecko)Chrome/120.0.0.0Safari/537.36"
      },
      "closed_at": "2024-01-12T03:48:28-05:00",
      "company": null,
      "confirmation_number": "DT9LFQPVA",
      "confirmed": true,
      "contact_email": "raj+1@valmi.io",
      "created_at": "2024-01-12T02:42:45-05:00",
      "currency": "INR",
      "current_subtotal_price": "0.00",
      "current_subtotal_price_set": {
        "shop_money": {
          "amount": "0.00",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "0.00",
          "currency_code": "INR"
        }
      },
      "current_total_additional_fees_set": null,
      "current_total_discounts": "0.00",
      "current_total_discounts_set": {
        "shop_money": {
          "amount": "0.00",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "0.00",
          "currency_code": "INR"
        }
      },
      "current_total_duties_set": null,
      "current_total_price": "0.00",
      "current_total_price_set": {
        "shop_money": {
          "amount": "0.00",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "0.00",
          "currency_code": "INR"
        }
      },
      "current_total_tax": "0.00",
      "current_total_tax_set": {
        "shop_money": {
          "amount": "0.00",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "0.00",
          "currency_code": "INR"
        }
      },
      "customer_locale": "en-IN",
      "device_id": null,
      "discount_codes": [
        {
          "code": "FREESHIP2024",
          "amount": "0.00",
          "type": "shipping"
        }
      ],
      "email": "raj+1@valmi.io",
      "estimated_taxes": false,
      "financial_status": "refunded",
      "fulfillment_status": null,
      "landing_site": "/password",
      "landing_site_ref": null,
      "location_id": null,
      "merchant_of_record_app_id": null,
      "name": "#1005",
      "note": null,
      "note_attributes": [],
      "number": 5,
      "order_number": 1005,
      "order_status_url": "https://quickstart-6ebc0909.myshopify.com/68875616470/orders/f15391ec8be8558cb9ba45c03ada0bd8/authenticate?key=bf91a312ff3be367bae5a03690b9a1e7",
      "original_total_additional_fees_set": null,
      "original_total_duties_set": null,
      "payment_gateway_names": [
        "bogus"
      ],
      "phone": null,
      "po_number": null,
      "presentment_currency": "INR",
      "processed_at": "2024-01-12T02:42:44-05:00",
      "reference": "00cb86adebfe522f3d333187f5abd96b",
      "referring_site": "",
      "source_identifier": "00cb86adebfe522f3d333187f5abd96b",
      "source_name": "web",
      "source_url": null,
      "subtotal_price": "2759.80",
      "subtotal_price_set": {
        "shop_money": {
          "amount": "2759.80",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "2759.80",
          "currency_code": "INR"
        }
      },
      "tags": "",
      "tax_exempt": false,
      "tax_lines": [
        {
          "price": "496.76",
          "rate": 0.18,
          "title": "IGST",
          "price_set": {
            "shop_money": {
              "amount": "496.76",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "496.76",
              "currency_code": "INR"
            }
          },
          "channel_liable": false
        }
      ],
      "taxes_included": false,
      "test": true,
      "token": "f15391ec8be8558cb9ba45c03ada0bd8",
      "total_discounts": "0.00",
      "total_discounts_set": {
        "shop_money": {
          "amount": "0.00",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "0.00",
          "currency_code": "INR"
        }
      },
      "total_line_items_price": "2759.80",
      "total_line_items_price_set": {
        "shop_money": {
          "amount": "2759.80",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "2759.80",
          "currency_code": "INR"
        }
      },
      "total_outstanding": "0.00",
      "total_price": "3256.56",
      "total_price_set": {
        "shop_money": {
          "amount": "3256.56",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "3256.56",
          "currency_code": "INR"
        }
      },
      "total_shipping_price_set": {
        "shop_money": {
          "amount": "0.00",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "0.00",
          "currency_code": "INR"
        }
      },
      "total_tax": "496.76",
      "total_tax_set": {
        "shop_money": {
          "amount": "496.76",
          "currency_code": "INR"
        },
        "presentment_money": {
          "amount": "496.76",
          "currency_code": "INR"
        }
      },
      "total_tip_received": "0.00",
      "total_weight": 0,
      "updated_at": "2024-01-12T04:36:00-05:00",
      "user_id": null,
      "billing_address": {
        "first_name": "raj",
        "address1": "210,Lakshmimegatownship,ragannaguda",
        "phone": null,
        "city": "Hyderabad",
        "zip": "501510",
        "province": "Telangana",
        "country": "India",
        "last_name": "Varkala",
        "address2": null,
        "company": null,
        "latitude": null,
        "longitude": null,
        "name": "rajVarkala",
        "country_code": "IN",
        "province_code": "TS"
      },
      "customer": {
        "id": 6971943256278,
        "email": "raj+1@valmi.io",
        "created_at": "2024-01-12T02:42:44-05:00",
        "updated_at": "2024-01-12T03:48:31-05:00",
        "first_name": "raj",
        "last_name": "Varkala",
        "state": "disabled",
        "note": null,
        "verified_email": true,
        "multipass_identifier": null,
        "tax_exempt": false,
        "phone": null,
        "email_marketing_consent": {
          "state": "not_subscribed",
          "opt_in_level": "single_opt_in",
          "consent_updated_at": null
        },
        "sms_marketing_consent": null,
        "tags": "",
        "currency": "INR",
        "tax_exemptions": [],
        "admin_graphql_api_id": "gid://shopify/Customer/6971943256278",
        "default_address": {
          "id": 8494931640534,
          "customer_id": 6971943256278,
          "first_name": "raj",
          "last_name": "Varkala",
          "company": null,
          "address1": "210,Lakshmimegatownship,ragannaguda",
          "address2": null,
          "city": "Hyderabad",
          "province": "Telangana",
          "country": "India",
          "zip": "501510",
          "phone": null,
          "name": "rajVarkala",
          "province_code": "TS",
          "country_code": "IN",
          "country_name": "India",
          "default": true
        }
      },
      "discount_applications": [
        {
          "target_type": "shipping_line",
          "type": "discount_code",
          "value": "100.0",
          "value_type": "percentage",
          "allocation_method": "each",
          "target_selection": "all",
          "code": "FREESHIP2024"
        }
      ],
      "fulfillments": [],
      "line_items": [
        {
          "id": 13347497050326,
          "admin_graphql_api_id": "gid://shopify/LineItem/13347497050326",
          "attributed_staffs": [],
          "current_quantity": 0,
          "fulfillable_quantity": 0,
          "fulfillment_service": "manual",
          "fulfillment_status": null,
          "gift_card": false,
          "grams": 0,
          "name": "TheMulti-managedSnowboard",
          "price": "629.95",
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
          "product_exists": true,
          "product_id": 8273463967958,
          "properties": [],
          "quantity": 2,
          "requires_shipping": true,
          "sku": "sku-managed-1",
          "taxable": true,
          "title": "TheMulti-managedSnowboard",
          "total_discount": "0.00",
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
          "variant_id": 44843037917398,
          "variant_inventory_management": "shopify",
          "variant_title": null,
          "vendor": "Multi-managedVendor",
          "tax_lines": [
            {
              "channel_liable": false,
              "price": "226.78",
              "price_set": {
                "shop_money": {
                  "amount": "226.78",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "226.78",
                  "currency_code": "INR"
                }
              },
              "rate": 0.18,
              "title": "IGST"
            }
          ],
          "duties": [],
          "discount_allocations": []
        },
        {
          "id": 13347497083094,
          "admin_graphql_api_id": "gid://shopify/LineItem/13347497083094",
          "attributed_staffs": [],
          "current_quantity": 0,
          "fulfillable_quantity": 0,
          "fulfillment_service": "manual",
          "fulfillment_status": null,
          "gift_card": false,
          "grams": 0,
          "name": "TheCollectionSnowboard:Liquid",
          "price": "749.95",
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
          "product_exists": true,
          "product_id": 8273464099030,
          "properties": [],
          "quantity": 2,
          "requires_shipping": true,
          "sku": "",
          "taxable": true,
          "title": "TheCollectionSnowboard:Liquid",
          "total_discount": "0.00",
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
          "variant_id": 44843038015702,
          "variant_inventory_management": "shopify",
          "variant_title": null,
          "vendor": "HydrogenVendor",
          "tax_lines": [
            {
              "channel_liable": false,
              "price": "269.98",
              "price_set": {
                "shop_money": {
                  "amount": "269.98",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "269.98",
                  "currency_code": "INR"
                }
              },
              "rate": 0.18,
              "title": "IGST"
            }
          ],
          "duties": [],
          "discount_allocations": []
        }
      ],
      "payment_terms": null,
      "refunds": [
        {
          "id": 887837196502,
          "admin_graphql_api_id": "gid://shopify/Refund/887837196502",
          "created_at": "2024-01-12T03:48:28-05:00",
          "note": "x",
          "order_id": 5364772372694,
          "processed_at": "2024-01-12T03:48:28-05:00",
          "restock": true,
          "total_duties_set": {
            "shop_money": {
              "amount": "0.00",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "0.00",
              "currency_code": "INR"
            }
          },
          "user_id": 89705382102,
          "order_adjustments": [],
          "transactions": [
            {
              "id": 6327309467862,
              "admin_graphql_api_id": "gid://shopify/OrderTransaction/6327309467862",
              "amount": "3256.56",
              "authorization": null,
              "created_at": "2024-01-12T03:48:27-05:00",
              "currency": "INR",
              "device_id": null,
              "error_code": null,
              "gateway": "bogus",
              "kind": "refund",
              "location_id": null,
              "message": "BogusGateway:Forcedsuccess",
              "order_id": 5364772372694,
              "parent_id": 6327269261526,
              "payment_id": "#1005.2",
              "processed_at": "2024-01-12T03:48:27-05:00",
              "receipt": {
                "paid_amount": "3256.56"
              },
              "source_name": "1830279",
              "status": "success",
              "test": true,
              "user_id": 89705382102,
              "payment_details": {
                "credit_card_bin": "1",
                "avs_result_code": null,
                "cvv_result_code": null,
                "credit_card_number": "••••••••••••1",
                "credit_card_company": "Bogus",
                "buyer_action_info": null,
                "credit_card_name": "VARKALARAJASHEKAR",
                "credit_card_wallet": null,
                "credit_card_expiration_month": 10,
                "credit_card_expiration_year": 2024,
                "payment_method_name": "bogus"
              }
            }
          ],
          "refund_line_items": [
            {
              "id": 450826502358,
              "line_item_id": 13347497050326,
              "location_id": 73971466454,
              "quantity": 2,
              "restock_type": "cancel",
              "subtotal": 1259.9,
              "subtotal_set": {
                "shop_money": {
                  "amount": "1259.90",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "1259.90",
                  "currency_code": "INR"
                }
              },
              "total_tax": 226.78,
              "total_tax_set": {
                "shop_money": {
                  "amount": "226.78",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "226.78",
                  "currency_code": "INR"
                }
              },
              "line_item": {
                "id": 13347497050326,
                "admin_graphql_api_id": "gid://shopify/LineItem/13347497050326",
                "attributed_staffs": [],
                "current_quantity": 0,
                "fulfillable_quantity": 0,
                "fulfillment_service": "manual",
                "fulfillment_status": null,
                "gift_card": false,
                "grams": 0,
                "name": "TheMulti-managedSnowboard",
                "price": "629.95",
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
                "product_exists": true,
                "product_id": 8273463967958,
                "properties": [],
                "quantity": 2,
                "requires_shipping": true,
                "sku": "sku-managed-1",
                "taxable": true,
                "title": "TheMulti-managedSnowboard",
                "total_discount": "0.00",
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
                "variant_id": 44843037917398,
                "variant_inventory_management": "shopify",
                "variant_title": null,
                "vendor": "Multi-managedVendor",
                "tax_lines": [
                  {
                    "channel_liable": false,
                    "price": "226.78",
                    "price_set": {
                      "shop_money": {
                        "amount": "226.78",
                        "currency_code": "INR"
                      },
                      "presentment_money": {
                        "amount": "226.78",
                        "currency_code": "INR"
                      }
                    },
                    "rate": 0.18,
                    "title": "IGST"
                  }
                ],
                "duties": [],
                "discount_allocations": []
              }
            },
            {
              "id": 450826535126,
              "line_item_id": 13347497083094,
              "location_id": 73971466454,
              "quantity": 2,
              "restock_type": "cancel",
              "subtotal": 1499.9,
              "subtotal_set": {
                "shop_money": {
                  "amount": "1499.90",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "1499.90",
                  "currency_code": "INR"
                }
              },
              "total_tax": 269.98,
              "total_tax_set": {
                "shop_money": {
                  "amount": "269.98",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "269.98",
                  "currency_code": "INR"
                }
              },
              "line_item": {
                "id": 13347497083094,
                "admin_graphql_api_id": "gid://shopify/LineItem/13347497083094",
                "attributed_staffs": [],
                "current_quantity": 0,
                "fulfillable_quantity": 0,
                "fulfillment_service": "manual",
                "fulfillment_status": null,
                "gift_card": false,
                "grams": 0,
                "name": "TheCollectionSnowboard:Liquid",
                "price": "749.95",
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
                "product_exists": true,
                "product_id": 8273464099030,
                "properties": [],
                "quantity": 2,
                "requires_shipping": true,
                "sku": "",
                "taxable": true,
                "title": "TheCollectionSnowboard:Liquid",
                "total_discount": "0.00",
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
                "variant_id": 44843038015702,
                "variant_inventory_management": "shopify",
                "variant_title": null,
                "vendor": "HydrogenVendor",
                "tax_lines": [
                  {
                    "channel_liable": false,
                    "price": "269.98",
                    "price_set": {
                      "shop_money": {
                        "amount": "269.98",
                        "currency_code": "INR"
                      },
                      "presentment_money": {
                        "amount": "269.98",
                        "currency_code": "INR"
                      }
                    },
                    "rate": 0.18,
                    "title": "IGST"
                  }
                ],
                "duties": [],
                "discount_allocations": []
              }
            }
          ],
          "duties": []
        }
      ],
      "shipping_address": {
        "first_name": "raj",
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
        "name": "rajVarkala",
        "country_code": "IN",
        "province_code": "TS"
      },
      "shipping_lines": [
        {
          "id": 4391570342102,
          "carrier_identifier": "650f1a14fa979ec5c74d063e968411d4",
          "code": "Standard",
          "discounted_price": "0.00",
          "discounted_price_set": {
            "shop_money": {
              "amount": "0.00",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "0.00",
              "currency_code": "INR"
            }
          },
          "phone": null,
          "price": "0.00",
          "price_set": {
            "shop_money": {
              "amount": "0.00",
              "currency_code": "INR"
            },
            "presentment_money": {
              "amount": "0.00",
              "currency_code": "INR"
            }
          },
          "requested_fulfillment_service_id": null,
          "source": "shopify",
          "title": "Standard",
          "tax_lines": [],
          "discount_allocations": [
            {
              "amount": "0.00",
              "amount_set": {
                "shop_money": {
                  "amount": "0.00",
                  "currency_code": "INR"
                },
                "presentment_money": {
                  "amount": "0.00",
                  "currency_code": "INR"
                }
              },
              "discount_application_index": 0
            }
          ]
        }
      ]
    }
;*/