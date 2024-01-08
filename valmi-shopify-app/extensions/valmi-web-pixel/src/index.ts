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
