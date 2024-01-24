/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 1:06:50 pm
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
    { "$.cart_token": { to: "$.cart_id" } },
    { "$.token": { to: "$.checkout_id" } },
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
    { "$.line_items[*].line_price": { to: "$.products[*].value" } },
    { "$.line_items[*].applied_discounts": { to: "$.products[*].coupon" } },
    { "$.line_items[*].vendor": { to: "$.products[*].brand" } },
  ];
};
export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  return [{
    fn: valmiAnalytics.track.bind(null, "Checkout Started - s2s"),
    mapping: mapping.bind(null, analytics_state),
    data: event,
  }]
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
const src = {
    id: 34309611520214,
    token: 'f25117962ca5a0f0f78896f36ca232a2',
    cart_token: 'Z2NwLXVzLWNlbnRyYWwxOjAxSEtZOUJXMDdHVldNNjBSWlZZVkUxQ1o3',
    email: null,
    gateway: null,
    buyer_accepts_marketing: false,
    buyer_accepts_sms_marketing: false,
    sms_marketing_phone: null,
    created_at: '2024-01-12T07:32:14+00:00',
    updated_at: '2024-01-12T02:35:33-05:00',
    landing_site: '/password',
    note: '',
    note_attributes: [],
    referring_site: '',
    shipping_lines: [],
    shipping_address: [],
    taxes_included: false,
    total_weight: 0,
    currency: 'INR',
    completed_at: null,
    phone: null,
    customer_locale: 'en-IN',
    line_items: [
      {
        key: '44843037917398',
        fulfillment_service: 'manual',
        gift_card: false,
        grams: 0,
        presentment_title: 'The Multi-managed Snowboard',
        presentment_variant_title: '',
        product_id: 8273463967958,
        quantity: 2,
        requires_shipping: true,
        sku: 'sku-managed-1',
        tax_lines: [Array],
        taxable: true,
        title: 'The Multi-managed Snowboard',
        variant_id: 44843037917398,
        variant_title: '',
        variant_price: '629.95',
        vendor: 'Multi-managed Vendor',
        unit_price_measurement: [Object],
        compare_at_price: null,
        line_price: '1259.90',
        price: '629.95',
        applied_discounts: [],
        destination_location_id: null,
        user_id: null,
        rank: null,
        origin_location_id: null,
        properties: null
      },
      {
        key: '44843038015702',
        fulfillment_service: 'manual',
        gift_card: false,
        grams: 0,
        presentment_title: 'The Collection Snowboard: Liquid',
        presentment_variant_title: '',
        product_id: 8273464099030,
        quantity: 2,
        requires_shipping: true,
        sku: '',
        tax_lines: [Array],
        taxable: true,
        title: 'The Collection Snowboard: Liquid',
        variant_id: 44843038015702,
        variant_title: '',
        variant_price: '749.95',
        vendor: 'Hydrogen Vendor',
        unit_price_measurement: [Object],
        compare_at_price: null,
        line_price: '1499.90',
        price: '749.95',
        applied_discounts: [],
        destination_location_id: null,
        user_id: null,
        rank: null,
        origin_location_id: null,
        properties: null
      }
    ],
    name: '#34309611520214',
    abandoned_checkout_url: 'https://quickstart-6ebc0909.myshopify.com/68875616470/checkouts/ac/Z2NwLXVzLWNlbnRyYWwxOjAxSEtZOUJXMDdecover?key=ed78a90c18cd1f17e9cd62e627426ba9',
    discount_codes: [],
    tax_lines: [ { price: '248.38', rate: 0.09, title: 'CGST' } ],
    presentment_currency: 'INR',
    source_name: 'web',
    total_line_items_price: '2759.80',
    total_tax: '248.38',
    total_discounts: '0.00',
    subtotal_price: '2759.80',
    total_price: '3008.18',
    total_duties: '0.00',
    device_id: null,
    user_id: null,
    location_id: null,
    source_identifier: null,
    source_url: null,
    source: null,
    closed_at: null
  };
  */