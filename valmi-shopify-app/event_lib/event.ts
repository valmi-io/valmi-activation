import { AnalyticsInterface } from "@jitsu/js";
import {mapping} from "./page_viewed";
export const event_handlers = (valmiAnalytics: AnalyticsInterface, event: any): any => {
    if (event.name == "page_viewed"){
        return {fn: valmiAnalytics.page, mapping};
    }
};