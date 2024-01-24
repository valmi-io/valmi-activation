export const createValmiConfig = async ({host, writeKey}: any) => {
  if (host && writeKey){
    return await prisma.valmiconf.upsert({
        where: {
          id: '0',
        },
        update: {
          writeKey: writeKey,
          host: host,
        },
        create: {
          id: '0',
          host: host,
          writeKey: writeKey,
        },
      })
  }
  return null;
};

export const getValmiConfig = async () => { 
    const val =  await prisma.valmiconf.findFirst({
        where: {
          id: '0',
        }
    })
    if (val){
      return val;
    }else{
      return {host: "", writeKey:""};
    }
};

export const getWebPixel = async(writeKey : string) => {
  const val = await prisma.webPixel.findFirst({
    where: {
      id: '0',
    }
  })
  if (val){
    return val;
  }else{
    return {id: "", pixel_id:""};
  }
}

export const storeWebPixel = async (pixel_id: string) => {
  return await prisma.webPixel.upsert({
      where: {
        id: '0',
      }, 
      create: {
        pixel_id: pixel_id,
        id: "0",
      },
      update:{
        pixel_id: pixel_id,
      }
    }) 
};
