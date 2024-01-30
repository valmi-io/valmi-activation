/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = (analytics_state: any): any => {
  return [  
    { "$.cart_token": { to: "$.cart_id" } },
    { "$.token": { to: "$.checkout_id" } },
    { "$.__shipping_method": { to: "$.shipping_method" } },
  ];
};

export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  if(event.shipping_lines.length > 0 && event.shipping_address){
    event.__shipping_method = event.shipping_lines[0].code;
    return [{
      fn: valmiAnalytics.track.bind(null, "Checkout Step Completed - s2s"),
      mapping: mapping.bind(null, analytics_state),
      data: event,
    }]
  }
  else{
    return [];
  }
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
const src =  {
  id: 34309611520214,
  token: 'f25117962ca5a0f0f78896f36ca232a2',
  cart_token: 'Z2NwLXVzLWNlbnRyYWwxOjAxSEtZOUJXMDdHVldNNjBSWlZZVkUxQ1o3',
  email: 'raj+1@valmi.io',
  gateway: null,
  buyer_accepts_marketing: false,
  buyer_accepts_sms_marketing: false,
  sms_marketing_phone: null,
  created_at: '2024-01-12T07:32:14+00:00',
  updated_at: '2024-01-12T02:41:04-05:00',
  landing_site: '/password',
  note: null,
  note_attributes: [],
  referring_site: '',
  shipping_lines: [
    {
      code: 'Standard',
      price: '0.00',
      original_shop_price: '0.00',
      original_shop_markup: '0.00',
      source: 'shopify',
      title: 'Standard',
      presentment_title: 'Standard',
      phone: null,
      tax_lines: [],
      custom_tax_lines: null,
      markup: '0.00',
      carrier_identifier: null,
      carrier_service_id: null,
      api_client_id: '580111',
      delivery_option_group: [Object],
      delivery_expectation_range: null,
      delivery_expectation_type: null,
      id: null,
      requested_fulfillment_service_id: null,
      delivery_category: null,
      validation_context: null,
      applied_discounts: []
    }
  ],
  shipping_address: {
    first_name: 'raj',
    address1: '210, Lakshmi mega township, ragannaguda',
    phone: null,
    city: 'Hyderabad',
    zip: '501510',
    province: 'Telangana',
    country: 'India',
    last_name: 'Varkala',
    address2: null,
    company: null,
    latitude: null,
    longitude: null,
    name: 'raj Varkala',
    country_code: 'IN',
    province_code: 'TS'
  },
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
  abandoned_checkout_url: 'https://quickstart-6ebc0909.myshopify.com/68875616470/checkouts/ac/Z2NwLXVzLWNlbnRyYWwxOjAxSEtZOUJXMDdcover?key=ed78a90c18cd1f17e9cd62e627426ba9',
  discount_codes: [ { code: 'FREESHIP2024', amount: '0.00', type: 'shipping' } ],
  tax_lines: [ { price: '496.76', rate: 0.18, title: 'IGST' } ],
  presentment_currency: 'INR',
  source_name: 'web',
  total_line_items_price: '2759.80',
  total_tax: '496.76',
  total_discounts: '0.00',
  subtotal_price: '2759.80',
  total_price: '3256.56',
  total_duties: '0.00',
  device_id: null,
  user_id: null,
  location_id: null,
  source_identifier: null,
  source_url: null,
  source: null,
  closed_at: null,
  billing_address: {
    first_name: 'raj',
    address1: '210, Lakshmi mega township, ragannaguda',
    phone: null,
    city: 'Hyderabad',
    zip: '501510',
    province: 'Telangana',
    country: 'India',
    last_name: 'Varkala',
    address2: null,
    company: null,
    latitude: null,
    longitude: null,
    name: 'raj Varkala',
    country_code: 'IN',
    province_code: 'TS'
  }
};*/