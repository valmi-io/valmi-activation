import type { LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { Form, useLoaderData } from "@remix-run/react";
import { login } from "../../shopify.server";
import indexStyles from "./style.css";

export const links = () => [{ rel: "stylesheet", href: indexStyles }];

export const loader = async ({ request }: LoaderFunctionArgs) => {
  const url = new URL(request.url);

  if (url.searchParams.get("shop")) {
    throw redirect(`/app?${url.searchParams.toString()}`);
  }

  return json({ showForm: Boolean(login) });
};

export default function App() {
  const { showForm } = useLoaderData<typeof loader>();

  return (
    <div className="index">
      <div className="content">
        <h1>valmi.io Customer Data Platform</h1>
        <p>Ingest User Activity Events, Unify Customer Data & Activate Data to engage with customers</p>
        {showForm && (
          <Form method="post" action="/auth/login">
            <label>
              <span>Shop domain</span>
              <input type="text" name="shop" />
              <span>e.g: my-shop-domain.myshopify.com</span>
            </label>
            <button type="submit">Log in</button>
          </Form>
        )}
        <ul>
          <li>
            <strong>User Event Tracking</strong>. Track & Ingest how user enagages with your shopify store.
          </li>
          <li>
            <strong>Create User Segments & Audiences</strong>. Create user segments based on user activity.
          </li>
          <li>
            <strong>Activate & Engage User Segments</strong>. Engage with users on different channels such as email, sms, push notifications etc.
          </li>
        </ul>
      </div>
    </div>
  );
}
