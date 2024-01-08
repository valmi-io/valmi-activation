/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Wednesday, January 3rd 2024, 10:20:04 pm
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

import type { HeadersFunction,ActionFunction, LoaderFunctionArgs, LoaderFunction } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, Outlet, useLoaderData, useRouteError ,useActionData, useSubmit} from "@remix-run/react";
import polarisStyles from "@shopify/polaris/build/esm/styles.css";
import { boundary, shopifyApp } from "@shopify/shopify-app-remix/server";
import { AppProvider } from "@shopify/shopify-app-remix/react";
import { apiVersion, authenticate, registerWebhooks, valmiHooks } from "../shopify.server";
import { useEffect } from "react";

export const links = () => [{ rel: "stylesheet", href: polarisStyles }];

export const loader = async ({ request }: LoaderFunctionArgs) => {
  await authenticate.admin(request);
  await webhookReregistration({request});
  return json({ apiKey: process.env.SHOPIFY_API_KEY || "" });
};

const verifyWebhookCreated = (data: any) => {
  const hookArr = Object.keys(valmiHooks).map((key) => {
    const lastIndex = key.lastIndexOf('_');
    const lc = key.toLowerCase();
    return lc.slice(0,lastIndex)+"/"+lc.slice(lastIndex+1);
  }); 

  const registeredHooks = Object.keys(data.data).map((key) => {
    return data.data[key]['topic'];
  });

  return hookArr.every((key) => {  
    console.log(key);
    if (registeredHooks.includes(key)){
      console.log("found webhook");
      return true;
    }
    else
    {
      console.log("webhook not found");
      return false;
    }
  }); 
}

export const webhookReregistration = async ({ request } : any) => {
  const  {admin, session} = await authenticate.admin(request);

  try{
    const data = await admin.rest.resources.Webhook.all({session: session});
    if(! verifyWebhookCreated(data)){
      // register webhooks again
      console.log("registering webhooks again");
      await registerWebhooks({session});
    }; 
  } catch(e){
    console.error(e);
  }
} 

export const action: ActionFunction = async ({request }) => {
  const {admin} = await authenticate.admin (request);
  // This mutation creates a web pixel, and sets the `accountID` declared in `shopify.extension.toml` to the value `234`.

  try{
    const response = await admin.graphql(
      `#graphql
      mutation {
        webPixelCreate(webPixel: { settings: {accountID: "234"} }) {
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
    )

    console.log(response);
    if(response.ok){
      const json = await response.json();
      console.log(json);
      return json;
    }
    else
    {
      console.log(response);
    }
    return null;
  }catch(e){
    console.error(e);
    console.log("mutation failed");
  }
  return null;
}

export default function App() {
  const { apiKey } = useLoaderData<typeof loader>();
  const actionData = useActionData<typeof action>();
  console.log(`actionData`, actionData);
  const submit = useSubmit();
  useEffect(() => {
    if(!actionData)
      submit({}, { method: "POST"});
  }
  , [actionData,submit]);


  return (
    <AppProvider isEmbeddedApp apiKey={apiKey}>
      <ui-nav-menu>
        <Link to="/app" rel="home">
          Home
        </Link>
        <Link to="/app/additional">Additional page</Link>
      </ui-nav-menu>
      <Outlet />
    </AppProvider>
  );
}

// Shopify needs Remix to catch some thrown responses, so that their headers are included in the response.
export function ErrorBoundary() {
  return boundary.error(useRouteError());
}

export const headers: HeadersFunction = (headersArgs) => {
  return boundary.headers(headersArgs);
};
