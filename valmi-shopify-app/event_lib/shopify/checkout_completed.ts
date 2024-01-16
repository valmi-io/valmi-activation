/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 11:07:15 am
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


/*
const src ={
    "id": "sh-fc30c49e-84C6-4C24-E319-88D1BB4479C2",
    "name": "checkout_completed",
    "data": {
        "checkout": {
            "attributes": [],
            "billingAddress": {
                "address1": "210, Lakshmi mega township, ragannaguda",
                "city": "Hyderabad",
                "country": "IN",
                "countryCode": "IN",
                "firstName": "Swathi",
                "lastName": "Varkala",
                "province": "TS",
                "provinceCode": "TS",
                "zip": "501510"
            },
            "token": "dd84dba9362eab31f3513ebd3bd82b6c",
            "currencyCode": "INR",
            "discountApplications": [
                {
                    "allocationMethod": "EACH",
                    "targetSelection": "ALL",
                    "targetType": "SHIPPING_LINE",
                    "title": "FREESHIP2024",
                    "type": "code",
                    "value": {
                        "percentage": 100
                    }
                }
            ],
            "email": "raj@mywavia.com",
            "lineItems": [
                {
                    "discountAllocations": [],
                    "id": "44843038015702",
                    "quantity": 1,
                    "title": "The Collection Snowboard: Liquid",
                    "variant": {
                        "id": "44843038015702",
                        "image": {
                            "src": "https://cdn.shopify.com/s/files/1/0688/7561/6470/products/Main_b13ad453-477c-4ed1-9b43-81f3345adfd6_64x64.jpg?v=1704619785"
                        },
                        "price": {
                            "amount": 749.95,
                            "currencyCode": "INR"
                        },
                        "product": {
                            "id": "8273464099030",
                            "title": "The Collection Snowboard: Liquid",
                            "vendor": "Hydrogen Vendor",
                            "type": "",
                            "untranslatedTitle": "The Collection Snowboard: Liquid",
                            "url": "/products/the-collection-snowboard-liquid"
                        },
                        "untranslatedTitle": ""
                    }
                }
            ],
            "order": {
                "id": "5364716830934"
            },
            "shippingAddress": {
                "address1": "210, Lakshmi mega township, ragannaguda",
                "city": "Hyderabad",
                "country": "IN",
                "countryCode": "IN",
                "firstName": "Swathi",
                "lastName": "Varkala",
                "province": "TS",
                "provinceCode": "TS",
                "zip": "501510"
            },
            "subtotalPrice": {
                "amount": 749.95,
                "currencyCode": "INR"
            },
            "shippingLine": {
                "price": {
                    "amount": 0,
                    "currencyCode": "INR"
                }
            },
            "totalTax": {
                "amount": 134.99,
                "currencyCode": "INR"
            },
            "totalPrice": {
                "amount": 884.94,
                "currencyCode": "INR"
            },
            "transactions": [
                {
                    "amount": {
                        "amount": 27.27,
                        "currencyCode": "EUR"
                    },
                    "gateway": "shopify_payments"
                }
            ]
        }
    },
    "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
    "timestamp": "2024-01-12T05:35:25.263Z",
    "context": {
        "document": {
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5/thank-you",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5/thank-you",
                "port": "",
                "protocol": "https:",
                "search": ""
            },
            "referrer": "https://quickstart-6ebc0909.myshopify.com/",
            "characterSet": "UTF-8",
            "title": "Checkout - Quickstart (6ebc0909)"
        },
        "navigator": {
            "language": "en-GB",
            "cookieEnabled": true,
            "languages": [
                "en-GB",
                "en-US",
                "en"
            ],
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        "window": {
            "innerHeight": 688,
            "innerWidth": 584,
            "outerHeight": 775,
            "outerWidth": 1235,
            "pageXOffset": 0,
            "pageYOffset": 0,
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5/thank-you",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtQOVRNQkcwU0czN0FZQTZIM0JWMDQ5/thank-you",
                "port": "",
                "protocol": "https:",
                "search": ""
            },
            "origin": "https://quickstart-6ebc0909.myshopify.com",
            "screen": {
                "height": 800,
                "width": 1280
            },
            "screenX": 0,
            "screenY": 25,
            "scrollX": 0,
            "scrollY": 0
        }
    }
};*/