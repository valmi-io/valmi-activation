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

register(({ configuration, analytics, browser }) => {

  const valmiAnalytics = jitsuAnalytics({
    host: "https://www.valmi.io",
    // Browser Write Key configured on Jitsu Site entity.
    // If no Browser Write Key is added for Site entity, Site ID value can be used a Write Key.
    // On Jitsu.Cloud can be omitted if Site has explicitly mapped domain name that is used in host parameter
    writeKey: "Yze5gDoyX2w8Kk5doGK0qF59sF6CHxkJ:************",
});
    // // Sample subscribe to page view
    // analytics.subscribe('page_viewed', (event) => {
    //   console.log('Page viewed', event);
    // });

  // Retrieve or set your tracking cookies
  //const uid = await browser.cookie.get('your_visitor_cookie');
  //const pixelEndpoint: string = `https://example.com/pixel?id=${settings.accountID}&uid=${uid}`;

  // Subscribe to events
  analytics.subscribe('all_events', (event) => {
    // Transform the event payload to fit your schema (optional)
     valmiAnalytics.track(event.name, {"myprop":JSON.stringify(event)});

  });
});
