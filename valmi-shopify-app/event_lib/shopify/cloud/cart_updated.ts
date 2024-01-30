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


const get_new_line_items =  (old_cart: any, new_cart:any) => {
  const copied_cart = {...new_cart};
  // overwrite line_items
  copied_cart.line_items =[];
  new_cart.line_items.forEach((element: any) => {
    if (old_cart.line_items.find((old_e: any) => old_e.key == element.key) == undefined){
      copied_cart.line_items.push(element);
    }
  });
  return copied_cart;
};

const get_removed_line_items =  (old_cart: any, new_cart:any) => {
  const copied_cart = {...new_cart};
  // overwrite line_items
  copied_cart.line_items =[];
  old_cart.line_items.forEach((element: any) => {
    if (old_cart.line_items.find((old_e: any) => old_e.key == element.key) == undefined){
      copied_cart.line_items.push(element);
    }
  });
  return copied_cart;
};

const get_quantity_added_items =  (old_cart: any, new_cart:any) => {
  const copied_cart = {...new_cart};
  // overwrite line_items
  copied_cart.line_items =[];
  new_cart.line_items.forEach((element: any) => {
    old_cart.line_items.forEach((old_e: any) => {
      if (old_e.key == element.key && element.quantity > old_e.quantity){
        const n_e = {...element};
        n_e.quantity = element.quantity - old_e.quantity;
        n_e.total_discount = element.total_discount - old_e.total_discount
        n_e.line_price = element.line_price - old_e.line_price;
        n_e.original_price = element.original_price - old_e.original_price;
        copied_cart.line_items.push(n_e);
      }
    });
  });
  return copied_cart;
};

const get_quantity_reduced_items =  (old_cart: any, new_cart:any) => {
  const copied_cart = {...new_cart};
  // overwrite line_items
  copied_cart.line_items =[];
  new_cart.line_items.forEach((element: any) => {
    old_cart.line_items.forEach((old_e: any) => {
      if (old_e.key == element.key && element.quantity < old_e.quantity){
        const n_e = {...element};
        n_e.quantity = old_e.quantity - element.quantity;
        n_e.total_discount = old_e.total_discount - element.total_discount
        n_e.line_price = old_e.line_price - element.line_price;
        n_e.original_price = old_e.original_price - element.original_price;
        copied_cart.line_items.push(n_e);
      }
    });
  });
  return copied_cart;
};

export const event_data = (valmiAnalytics: AnalyticsInterface, analytics_state: any, event: any) : any => {
  // get cart_token
  // get last cart data from analytics_state
  // diff it to figure out Product Added or Product Removed


  const cart_token = event.token;
  let cart: any = analytics_state.findCartByToken(cart_token);
  console.log("old cart", cart);
  if (!cart){
    cart = {line_items:[]};
  }
  //update cart
  analytics_state.updateCart(cart_token, event);

  console.log("cart", cart);
  console.log("event", event);
  
  const new_line_items = get_new_line_items(cart,event);
  const removed_line_items = get_removed_line_items(cart,event);
  const quantity_added_items = get_quantity_added_items(cart, event);
  const quantity_reduced_items = get_quantity_reduced_items(cart, event);
  console.log("new_line_items", new_line_items);  
  console.log("removed_line_items", removed_line_items);
  console.log("quantity_added_items", quantity_added_items);
  console.log("quantity_reduced_items", quantity_reduced_items);


  const ret: any[] = [];
  new_line_items.line_items.forEach((element: any) => {
    const sub_item = {...new_line_items};
    sub_item.line_item = element;
    ret.push({
      fn: valmiAnalytics.track.bind(null, "Product Added - s2s"),
      mapping: mapping.bind(null, analytics_state),
      data: sub_item,
    }); 
  });
  removed_line_items.line_items.forEach((element: any) => {
    const sub_item = {...removed_line_items};
    sub_item.line_item = element;
    ret.push({
      fn: valmiAnalytics.track.bind(null, "Product Removed - s2s"),
      mapping: mapping.bind(null, analytics_state),
      data: sub_item,
    }); 
  });
  quantity_added_items.line_items.forEach((element: any) => {
    const sub_item = {...quantity_added_items};
    sub_item.line_item = element;
    ret.push({
      fn: valmiAnalytics.track.bind(null, "Product Added - s2s"),
      mapping: mapping.bind(null, analytics_state),
      data: sub_item,
    }); 
  });
  quantity_reduced_items.line_items.forEach((element: any) => {
    const sub_item = {...quantity_reduced_items};
    sub_item.line_item = element;
    ret.push({
      fn: valmiAnalytics.track.bind(null, "Product Removed - s2s"),
      mapping: mapping.bind(null, analytics_state),
      data: sub_item,
    }); 
  });
  return ret;
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.track;

/*
analytics.track('Product Removed', {
  cart_id: 'ksjdj92dj29dj92d2j',
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
    id: "Z2NwLXVzLWNlbnRyYWwxOjAxSEtZMllEN0NZTkEwRVo3QlpHMkUyMEo4",
    token: "Z2NwLXVzLWNlbnRyYWwxOjAxSEtZMllEN0NZTkEwRVo3QlpHMkUyMEo4",
    line_items: [
      {
        id: 44843037917398,
        properties: null,
        quantity: 2,
        variant_id: 44843037917398,
        key: "44843037917398:eadbd69080be0fc12bb7f4f45e8cba36",
        discounted_price: "629.95",
        discounts: [],
        gift_card: false,
        grams: 0,
        line_price: "1259.90",
        original_line_price: "1259.90",
        original_price: "629.95",
        price: "629.95",
        product_id: 8273463967958,
        sku: "sku-managed-1",
        taxable: true,
        title: "TheMulti-managedSnowboard",
        total_discount: "0.00",
        vendor: "Multi-managedVendor",
        discounted_price_set: {
          shop_money: { amount: "629.95", currency_code: "INR" },
          presentment_money: { amount: "629.95", currency_code: "INR" },
        },
        line_price_set: {
          shop_money: { amount: "1259.9", currency_code: "INR" },
          presentment_money: { amount: "1259.9", currency_code: "INR" },
        },
        original_line_price_set: {
          shop_money: { amount: "1259.9", currency_code: "INR" },
          presentment_money: { amount: "1259.9", currency_code: "INR" },
        },
        price_set: {
          shop_money: { amount: "629.95", currency_code: "INR" },
          presentment_money: { amount: "629.95", currency_code: "INR" },
        },
        total_discount_set: {
          shop_money: { amount: "0.0", currency_code: "INR" },
          presentment_money: { amount: "0.0", currency_code: "INR" },
        },
      },
      {
        id: 44843038015702,
        properties: null,
        quantity: 1,
        variant_id: 44843038015702,
        key: "44843038015702:924e31e59aecfb44d43f64d4d6f83b1f",
        discounted_price: "749.95",
        discounts: [],
        gift_card: false,
        grams: 0,
        line_price: "749.95",
        original_line_price: "749.95",
        original_price: "749.95",
        price: "749.95",
        product_id: 8273464099030,
        sku: "",
        taxable: true,
        title: "TheCollectionSnowboard:Liquid",
        total_discount: "0.00",
        vendor: "HydrogenVendor",
        discounted_price_set: {
          shop_money: { amount: "749.95", currency_code: "INR" },
          presentment_money: { amount: "749.95", currency_code: "INR" },
        },
        line_price_set: {
          shop_money: { amount: "749.95", currency_code: "INR" },
          presentment_money: { amount: "749.95", currency_code: "INR" },
        },
        original_line_price_set: {
          shop_money: { amount: "749.95", currency_code: "INR" },
          presentment_money: { amount: "749.95", currency_code: "INR" },
        },
        price_set: {
          shop_money: { amount: "749.95", currency_code: "INR" },
          presentment_money: { amount: "749.95", currency_code: "INR" },
        },
        total_discount_set: {
          shop_money: { amount: "0.0", currency_code: "INR" },
          presentment_money: { amount: "0.0", currency_code: "INR" },
        },
      },
    ],
    note: "",
    updated_at: "2024-01-13T10:00:09.104Z",
    created_at: "2024-01-12T05:40:01.640Z",
  }
};
*/