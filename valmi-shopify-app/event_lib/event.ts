/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
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
import { mapping as product_added_mapping } from "./shopify/product_added_to_cart";
import { mapping as product_removed_mapping } from "./shopify/product_removed_from_cart";
import { mapping as checkout_started_mapping } from "./shopify/checkout_started";
import { track_mapping as checkout_address_info_track_mapping } from "./shopify/checkout_address_info_submitted";
import { track_mapping as checkout_contact_info_track_mapping } from "./shopify/checkout_contact_info_submitted";
import { track_mapping as checkout_shipping_info_track_mapping } from "./shopify/checkout_shipping_info_submitted";
import { track_mapping as checkout_completed_track_mapping } from "./shopify/checkout_completed";

import { event_data as cart_created_event_data } from "./shopify/cloud/cart_created";
import { event_data as cart_updated_event_data } from "./shopify/cloud/cart_updated";
import { event_data as customers_created_event_data } from "./shopify/cloud/customer_created";
import { event_data as customers_updated_event_data } from "./shopify/cloud/customer_updated";
import { event_data as checkouts_created_event_data } from "./shopify/cloud/checkout_created";
import { event_data as checkouts_updated_event_data } from "./shopify/cloud/checkout_updated";
import { event_data as orders_created_event_data } from "./shopify/cloud/order_created";
import { event_data as orders_cancelled_event_data } from "./shopify/cloud/order_cancelled";
import { event_data as refunds_created_event_data } from "./shopify/cloud/refund_created";
import { event_data as fulfillments_created_event_data } from "./shopify/cloud/fulfillment_created";
import { event_data as fulfillments_updated_event_data } from "./shopify/cloud/fulfillment_updated";

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
      {
        fn: valmiAnalytics.track.bind(null, "Checkout Step Completed"),
        mapping: checkout_address_info_track_mapping,
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
      {
        fn: valmiAnalytics.track.bind(null, "Checkout Step Completed"),
        mapping: checkout_contact_info_track_mapping,
        data: event,
      },
    ];
  } else if (event.name == "checkout_shipping_info_submitted") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Checkout Step Completed"),
        mapping: checkout_shipping_info_track_mapping,
        data: event,
      },
    ];
  } else if (event.name == "product_added_to_cart") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Product Added"),
        mapping: product_added_mapping,
        data: event,
      },
    ];
  } else if (event.name == "product_removed_from_cart") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Product Removed"),
        mapping: product_removed_mapping,
        data: event,
      },
    ];
  } else if (event.name == "checkout_started") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Checkout Started"),
        mapping: checkout_started_mapping,
        data: event,
      },
    ];
  } else if (event.name == "checkout_completed") {
    return [
      {
        fn: valmiAnalytics.track.bind(null, "Order Completed"),
        mapping: checkout_completed_track_mapping,
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
  } 
    else if (event.topic == "ORDERS_CREATE") {
    return orders_created_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "ORDERS_CANCELLED") {
    return orders_cancelled_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "REFUNDS_CREATE") {
    return refunds_created_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "FULFILLMENTS_CREATE") {
    return fulfillments_created_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "FULFILLMENTS_UPDATE") {
    return fulfillments_updated_event_data(valmiAnalytics, analytics_state, event);
  } /* DO NOT DO IDENTIFY FROM SERVER SIDE
    else if (event.topic == "CUSTOMERS_CREATE") {
    return customers_created_event_data(valmiAnalytics, analytics_state, event);
  } else if (event.topic == "CUSTOMERS_UPDATE") {
    return customers_updated_event_data(valmiAnalytics, analytics_state, event);
  } */ else {
    return [{ fn: () => {}, mapping: () => [] }];
  }
};
