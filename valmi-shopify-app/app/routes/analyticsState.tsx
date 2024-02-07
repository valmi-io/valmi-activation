/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

const carts: any = {}; // TODO: use a database

export const analytics_state = () => {
  return {
    findCartByToken: (token: string) => {
      // console.log("find carts", carts);

      if (carts.hasOwnProperty(token)) {
        return carts[token];
      }
      return null;
    },
    updateCart: (token: string, cart: any) => {
      carts[token] = cart;
      // console.log("carts", carts);
    },
  };
};

export const writeKeyTovalmiAnalyticsMap: any = {};
