/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Wednesday, January 3rd 2024, 10:41:59 pm
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

import {register} from "@shopify/web-pixels-extension";
import {jitsuAnalytics} from "@jitsu/js";
import {transform} from "../../../event_lib/transformer";

register(({ configuration, analytics, browser, init }) => {

  const valmiAnalytics = jitsuAnalytics({
    host: "https://www.mywavia.com",
    writeKey: "Yze5gDoyX2w8Kk5doGK0qF59sF6CHxkJ:************",
}); 
  // Subscribe to events
  analytics.subscribe('all_events', (event) => {
    console.log("event",event);

    // To capture PAYMENT FAILED event, we need to credit the theme app extension and edit the liquid file.
    // And then publish a custom pixel event and then subscribe to it on the custom pixel .
    // https://shopify.dev/docs/api/admin-graphql/2024-04/mutations/webPixelCreate
    // https://help.shopify.com/en/manual/promoting-marketing/pixels/custom-pixels/code
    // https://help.shopify.com/en/manual/promoting-marketing/pixels/custom-pixels#custom-pixel-setup

    transform(valmiAnalytics, event, {});
  });
});
