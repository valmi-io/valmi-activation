/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { AnalyticsInterface } from "@jitsu/js";

export const mapping = (analytics_state: any): any => {
  return [  
    { "$.token": { to: "$.cart_id" } },
    { "$.line_item.product_id": { to: "$.product_id" } },
    { "$.line_item.sku": { to: "$.product_id" } },
    { "$.line_item.title": { to: "$.name" } },
    { "$.line_item.vendor": { to: "$.brand" } },
    { "$.line_item.quantity": { to: "$.quantity" } },
    { "$.line_item.original_price": { to: "$.price" } },
    { "$.line_item.discounts": { to: "$.coupon" } },
    { "$.line_item.line_price": { to: "$.value" } },
    { "$.line_item.total_discount": { to: "$.discount_value" } },  
    { "$.line_item.price_set.presentment_money.currency_code": { to: "$.currency" } }, 
  ];
};
export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  
  //update cart
  analytics_state.updateCart(event.token, event);
  
  if(event.line_items.length > 0){
    event.line_item = event.line_items[0];
    return [{
      fn: valmiAnalytics.track.bind(null, "Product Added - s2s"),
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
analytics.track('Product Added', {
  cart_id: 'skdjsidjsdkdj29j',
  product_id: '507f1f77bcf86cd799439011',
  sku: 'G-32',
  category: 'Games',
  name: 'Monopoly: 3rd Edition',
  brand: 'Hasbro',
  variant: '200 pieces',
  price: 18.99,
  quantity: 1,
  coupon: 'MAYDEALS',
  position: 3,
  url: 'https://www.example.com/product/path',
  image_url: 'https://www.example.com/product/path.jpg'
});

const src = { 
    id: 'Z2NwLXVzLWNlbnRyYWwxOjAxSEtZOUJXMDdHVldNNjBSWlZZVkUxQ1o3',
    token: 'Z2NwLXVzLWNlbnRyYWwxOjAxSEtZOUJXMDdHVldNNjBSWlZZVkUxQ1o3',
    line_items: [
      {
        id: 44843038015702, 
        properties: null,
        quantity: 1,
        variant_id: 44843038015702,
        key: '44843038015702:924e31e59aecfb44d43f64d4d6f83b1f',
        discounted_price: '749.95',
        discounts: [],
        gift_card: false,
        grams: 0,
        line_price: '749.95',   
        original_line_price: '749.95', 
        original_price: '749.95',
        price: '749.95',
        product_id: 8273464099030,
        sku: '',
        taxable: true,
        title: 'The Collection Snowboard: Liquid',
        total_discount: '0.00', 
        vendor: 'Hydrogen Vendor',
        discounted_price_set: [Object],
        line_price_set: [Object],
        original_line_price_set: [Object],
        price_set: [Object],    
        total_discount_set: [Object]
      }
    ],
    note: '',
    updated_at: '2024-01-12T07:32:14.142Z',
    created_at: '2024-01-12T07:32:14.142Z'
  };
*/