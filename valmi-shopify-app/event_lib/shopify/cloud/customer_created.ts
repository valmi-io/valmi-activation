/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 1:15:58 pm
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
    updated_at: '2024-01-12T02:42:44-05:00',
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
    addresses: [],
    tax_exemptions: [],
    email_marketing_consent: {
      state: 'not_subscribed',
      opt_in_level: 'single_opt_in',
      consent_updated_at: null
    },
    sms_marketing_consent: null,
    admin_graphql_api_id: 'gid://shopify/Customer/6971943256278'
  };*/