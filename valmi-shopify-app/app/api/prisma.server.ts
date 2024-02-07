/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

export const createValmiConfig = async ({shop, host, writeKey}: any) => {
  if (host && writeKey){
    return await prisma.valmiconf.upsert({
        where: {
          id: shop,
        },
        update: {
          writeKey: writeKey,
          host: host,
        },
        create: {
          id: shop,
          host: host,
          writeKey: writeKey,
        },
      })
  }
  return null;
};

export const deleteValmiConfig = async (shop: string) => {
  return await prisma.valmiconf.delete({
      where: {
        id: shop,
      }
    })
};

export const getValmiConfig = async (shop: string) => { 
    const val =  await prisma.valmiconf.findFirst({
        where: {
          id: shop,
        }
    })
    if (val){
      return val;
    }else{
      return {host: "", writeKey:""};
    }
};

export const getWebPixel = async(shop : string) => {
  const val = await prisma.webPixel.findFirst({
    where: {
      id: shop,
    }
  })
  if (val){
    return val;
  }else{
    return {id: "", pixel_id:""};
  }
}

export const storeWebPixel = async (shop : string, pixel_id: string) => {
  return await prisma.webPixel.upsert({
      where: {
        id: shop,
      }, 
      create: {
        pixel_id: pixel_id,
        id: shop,
      },
      update:{
        pixel_id: pixel_id,
      }
    }) 
};

export const deleteWebPixel = async (shop: string) => {
  return await prisma.webPixel.delete({
      where: {
        id: shop,
      }
    })
}

