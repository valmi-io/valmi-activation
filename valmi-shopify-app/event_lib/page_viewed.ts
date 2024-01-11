import { AnalyticsInterface } from "@jitsu/js";

export const mapping = () : any => {
    return {
      "$.context.document.title":{to: "$.title"},
      "$.context.document.location.href": {to: "$.url"},
      "$.context.document.referrer": {to: "$.referrer"},
      "$.context.document.location.pathname": {to: "$.path"},
      "$.context.document.location.search": {to: "$.search"},
    };
};

export const fn = (valmiAnalytics: AnalyticsInterface) => valmiAnalytics.page;