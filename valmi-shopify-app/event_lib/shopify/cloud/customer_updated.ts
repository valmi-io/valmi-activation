/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";
import { ignoreIfEmpty } from "event_lib/common";

export const mapping = () : any => {
    return [
      {"$.email":{to: "$.email" , beforeUpdate: ignoreIfEmpty}},
      {"$.phone": {to: "$.phone", beforeUpdate: ignoreIfEmpty}},
      {"$.first_name": {to: "$.firstName", beforeUpdate: ignoreIfEmpty}},
      {"$.last_name": {to: "$.lastName", beforeUpdate: ignoreIfEmpty}},
    ];
};

export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
   
    return [{
      fn: valmiAnalytics.identify.bind(null, event.id.toString().repeat(1)),
      mapping: mapping,
      data: event,
    }];
}; 
/*
const src = {
    id: 6971943256278,
    email: 'raj+1@valmi.io',
    created_at: '2024-01-12T02:42:44-05:00',
    updated_at: '2024-01-12T02:42:46-05:00',
    first_name: 'raj',
    last_name: 'Varkala',
    orders_count: 0,
    state: 'disabled',
    total_spent: '0.00',
    last_order_id: null,
    note: null,
    verified_email: true,
    multipass_identifier: null,
    tax_exempt: false,
    tags: '',
    last_order_name: null,
    currency: 'INR',
    phone: null,
    addresses: [
      {
        id: 8494931640534,
        customer_id: 6971943256278,
        first_name: 'raj',
        last_name: 'Varkala',
        company: null,
        address1: '210, Lakshmi mega township, ragannaguda',
        address2: null,
        city: 'Hyderabad',
        province: 'Telangana',
        country: 'India',
        zip: '501510',
        phone: null,
        name: 'raj Varkala',
        province_code: 'TS',
        country_code: 'IN',
        country_name: 'India',
        default: true
      }
    ],
    tax_exemptions: [],
    email_marketing_consent: {
      state: 'not_subscribed',
      opt_in_level: 'single_opt_in',
      consent_updated_at: null
    },
    sms_marketing_consent: null,
    admin_graphql_api_id: 'gid://shopify/Customer/6971943256278',
    default_address: {
      id: 8494931640534,
      customer_id: 6971943256278,
      first_name: 'raj',
      last_name: 'Varkala',
      company: null,
      address1: '210, Lakshmi mega township, ragannaguda',
      address2: null,
      city: 'Hyderabad',
      province: 'Telangana',
      country: 'India',
      zip: '501510',
      phone: null,
      name: 'raj Varkala',
      province_code: 'TS',
      country_code: 'IN',
      country_name: 'India',
      default: true
    }
  };  */