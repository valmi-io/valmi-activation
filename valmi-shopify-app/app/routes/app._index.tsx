/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io/valmi-activation>

 * Created Date: Wednesday, January 24th 2024, 4:23:32 am
 * Author: Rajashekar Varkala @ valmi.io
 */

import { useEffect, useState } from "react";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { Form, useActionData, useLoaderData, useNavigation, useSubmit } from "@remix-run/react";
import {
  Page,
  Layout,
  Text,
  Card,
  BlockStack,
  TextField,
  Button,
} from "@shopify/polaris";
import { authenticate } from "../shopify.server";
import { createValmiConfig, getValmiConfig, getWebPixel, storeWebPixel } from "~/api/prisma.server";

export const loader = async ({ request }: LoaderFunctionArgs) => {
  await authenticate.admin(request);
  try { 
    const val = await getValmiConfig();
    return val;
  } catch (err) {
    console.log(err);
  }
};

 

const webPixelUpdate = async ({admin,host,writeKey}:any) => {
  try{
    const pixel: any = await getWebPixel(writeKey);
    //console.log(pixel);
    // webpixel  does not exist
    if( ! pixel.pixel_id){ 
      const response = await admin.graphql(
        `#graphql
        mutation {
          webPixelCreate(webPixel: { settings: {host:"${host}", writeKey: "${writeKey}" } }) {
            userErrors {
              code
              field
              message
            }
            webPixel {
              settings
              id
            }
          }
        }

        `
      ); 
      //console.log(response);
      if(response.ok){
        const json = await response.json();
        console.log(JSON.stringify(json)); 
        if(json?.data?.webPixelCreate?.webPixel?.id){
          await storeWebPixel(json.data.webPixelCreate.webPixel.id);
        }
        return json;
      }
      else
      {
        console.log(response);
      }
      return null;
    } else { 
      const response = await admin.graphql(
        `#graphql
        mutation {
          webPixelUpdate( id: "${pixel.pixel_id}",  webPixel: { settings: {host:"${host}", writeKey: "${writeKey}" } }) {
            userErrors {
              code
              field
              message
            }
            webPixel {
              settings
              id
            }
          }
        }
        `
      ); 
      //console.log(response);
      if(response.ok){
        const json = await response.json();
        console.log(JSON.stringify(json)); 
        if(json?.data?.webPixelCreate?.webPixel?.id){
          await storeWebPixel(json.data.webPixelCreate.webPixel.id);
        }
        return json;
      }
      else
      {
        console.log(response);
      }
      return null;
    }

  }catch(e){
    console.error(e);
    console.log("mutation failed");
  }
  return null;
}

export const action = async ({ request }: ActionFunctionArgs) => {
  const { admin } = await authenticate.admin(request);

  const formData = await request.formData();
  const host = formData.get("host");
  const writeKey = formData.get("writeKey");
  try {
    const val = await createValmiConfig({host, writeKey});


    // Update Webpixel configuration
    if(! webPixelUpdate({admin,host,writeKey}))
      return null;

    return val;
  } catch (err) {
    console.log(err);
  }
  return null;
};

export default function Index() {
  const storedConfig = useLoaderData<typeof loader>();

  const nav = useNavigation();
  const actionData = useActionData<typeof action>();
  const submit = useSubmit();


  const isLoading =
    ["loading", "submitting"].includes(nav.state) && nav.formMethod === "POST";

  const actiondata_host = actionData?.host;
  const actiondata_writeKey = actionData?.writeKey;

  useEffect(() => {
    if (actiondata_host || actiondata_writeKey) {
      shopify.toast.show("valmi.io Configuration Updated");
    }
  }, [actiondata_host, actiondata_writeKey]);

  const generateConfiguration = () =>
    submit({}, { replace: true, method: "POST" });

  if(!storedConfig){
    return (<> </>);
  }
  const [host, setHost] = useState(storedConfig.host);
  const [writeKey, setWriteKey] = useState(storedConfig.writeKey);
  return (
    <Page>
      <ui-title-bar title="valmi.io Customer Data Platform">
      </ui-title-bar>
      <BlockStack gap="500">
        <Layout>
          <Layout.Section>
            <Card>
              <BlockStack gap="200">
                <Text as="h2" variant="headingMd">
                  Please configure your valmi.io account
                </Text>
                  <Form onSubmit={generateConfiguration} method="post">

                    <TextField
                      id="host"
                      name="host"
                      label="Host"
                      autoComplete="off"
                      value={host}
                      onChange={(value) => setHost(value)}
                    ></TextField>
                    <br />
                    <TextField
                      id="writeKey"
                      name="writeKey"
                      label="Write Key"
                      autoComplete="off"
                      value={writeKey}
                      onChange={(value) => setWriteKey(value)}
                    ></TextField>
                    <br/>
                    <Button submit loading={isLoading}> Submit </Button>

                  </Form>
              </BlockStack>
            </Card>
          </Layout.Section>
        </Layout>
      </BlockStack>
    </Page>
  );
}
