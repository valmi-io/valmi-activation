/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 *
 * Created Date: Thursday, January 11th 2024, 1:30:30 pm
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
import { mapping as pv_mapping } from "./shopify/page_viewed";
import { mapping as product_viewed_mapping } from "./shopify/product_viewed";
import { mapping as search_submitted_mapping } from "./shopify/search_submitted";
import { mapping as collection_viewed_mapping } from "./shopify/collection_viewed";
import { mapping as cart_viewed_mapping } from "./shopify/cart_viewed";
import { mapping as checkout_address_info_mapping } from "./shopify/checkout_address_info_submitted";
import { fn as address_info_fn } from "./shopify/checkout_address_info_submitted";
import { mapping as checkout_contact_info_mapping } from "./shopify/checkout_contact_info_submitted";
import { fn as contact_info_fn } from "./shopify/checkout_address_info_submitted";

import { event_data as cart_created_event_data } from "./shopify/cloud/cart_created";
import { event_data as cart_updated_event_data } from "./shopify/cloud/cart_updated";
import { event_data as customers_created_event_data } from "./shopify/cloud/customer_created";
import { event_data as customers_updated_event_data } from "./shopify/cloud/customer_updated";
import { event_data as checkouts_created_event_data } from "./shopify/cloud/checkout_created";
import { event_data as checkouts_updated_event_data } from "./shopify/cloud/checkout_updated";

export const event_handlers = (
  valmiAnalytics: AnalyticsInterface,
  event: any,
  analytics_state: any
): any => {
  if (event.name == "page_viewed") {
    return [{ fn: valmiAnalytics.page, mapping: pv_mapping, data: event }];
  } else if (event.name == "product_viewed") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Product Viewed"),
        mapping: product_viewed_mapping,
        data: event,
      },
    ];
  } else if (event.name == "search_submitted") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Products Searched"),
        mapping: search_submitted_mapping,
        data: event,
      },
    ];
  } else if (event.name == "collection_viewed") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Product List Viewed"),
        mapping: collection_viewed_mapping,
        data: event,
      },
    ];
  } else if (event.name == "cart_viewed") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Cart Viewed"),
        mapping: cart_viewed_mapping,
        data: event,
      },
    ];
  } else if (event.name == "checkout_address_info_submitted") {
    return [
      {
        fn: address_info_fn(valmiAnalytics),
        mapping: checkout_address_info_mapping,
        data: event,
      },
    ];
  } else if (event.name == "checkout_contact_info_submitted") {
    return [
      {
        fn: contact_info_fn(valmiAnalytics),
        mapping: checkout_contact_info_mapping,
        data: event,
      },
    ];
  }  
  
  else if (event.topic == "CARTS_CREATE") {
    return cart_created_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "CARTS_UPDATE") {
    return cart_updated_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "CHECKOUTS_CREATE") {
    return checkouts_created_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "CHECKOUTS_UPDATE") {
    return checkouts_updated_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "CUSTOMERS_CREATE") {
    return customers_created_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "CUSTOMERS_UPDATE") {
    return customers_updated_event_data(valmiAnalytics, analytics_state, event);
  } else {
    return [{ fn: () => {}, mapping: () => [] }];
  }
};
