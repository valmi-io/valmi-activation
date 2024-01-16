const carts: any = {};
export const analytics_state = () => {
  return {
    findCartByToken: (token: string) => {
      console.log("find carts", carts);

      if (carts.hasOwnProperty(token)) {
        return carts[token];
      }
      return null;
    },
    updateCart: (token: string, cart: any) => {
      carts[token] = cart;
      console.log("carts", carts);
    },
  };
};
