/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 2:15:19 pm
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
  ];
};
export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  return [{
    fn: valmiAnalytics.track.bind(null, "Fulfillment Created - s2s"),
    mapping: mapping.bind(null, analytics_state),
    data: event,
  }]
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
const src ={
    id: 4829428613334,
    order_id: 5364786725078,
    status: 'success',
    created_at: '2024-01-12T03:44:36-05:00',
    service: 'manual',
    updated_at: '2024-01-12T03:44:36-05:00',
    tracking_company: '4PX',
    shipment_status: null,
    location_id: 73971466454,
    origin_address: null,
    email: 'raj@mywavia.com',
    destination: {
      first_name: 'Swathi',
      address1: '210, Lakshmi mega township, ragannaguda',
      phone: null,
      city: 'Hyderabad',
      zip: '501510',
      province: 'Telangana',
      country: 'India',
      last_name: 'Varkala',
      address2: null,
      company: null,
      latitude: 17.2629066,
      longitude: 78.5860155,
      name: 'Swathi Varkala',
      country_code: 'IN',
      province_code: 'TS'
    },
    line_items: [
      {
        id: 13347521822934,
        variant_id: 44843038015702,
        title: 'The Collection Snowboard: Liquid',
        quantity: 1,
        sku: '',
        variant_title: null,
        vendor: 'Hydrogen Vendor',
        fulfillment_service: 'manual',
        product_id: 8273464099030,
        requires_shipping: true,
        taxable: true,
        gift_card: false,
        name: 'The Collection Snowboard: Liquid',
        variant_inventory_management: 'shopify',
        properties: [],
        product_exists: true,
        fulfillable_quantity: 0,
        grams: 0,
        price: '749.95',
        total_discount: '0.00',
        fulfillment_status: 'fulfilled',
        price_set: [Object],
        total_discount_set: [Object],
        discount_allocations: [],
        duties: [],
        admin_graphql_api_id: 'gid://shopify/LineItem/13347521822934',
        tax_lines: [Array]
      }
    ],
    tracking_number: '21',
    tracking_numbers: [ '21' ],
    tracking_url: 'http://track.4px.com',
    tracking_urls: [ 'http://track.4px.com' ],
    receipt: {},
    name: '#1006.1',
    admin_graphql_api_id: 'gid://shopify/Fulfillment/4829428613334'
  }; */