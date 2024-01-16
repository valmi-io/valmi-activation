/*
 * Copyright (c) 2024 valmi.io <https://github.com/valmi-io>
 * 
 * Created Date: Friday, January 12th 2024, 11:02:17 am
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
const src = {
    "id": "sh-11b979bf-75E0-48FB-05C1-67712D9FE7FD",
    "name": "checkout_shipping_info_submitted",
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
                "phone": "",
                "province": "TS",
                "provinceCode": "TS",
                "zip": "501510"
            },
            "token": "5edf493efb3e6e89f71d6126920dc723",
            "currencyCode": "INR",
            "discountApplications": [],
            "email": "raj@mywavia.com",
            "phone": "",
            "lineItems": [
                {
                    "discountAllocations": [],
                    "id": "44843037917398",
                    "quantity": 3,
                    "title": "The Multi-managed Snowboard",
                    "variant": {
                        "id": "44843037917398",
                        "image": {
                            "src": "https://cdn.shopify.com/s/files/1/0688/7561/6470/products/Main_9129b69a-0c7b-4f66-b6cf-c4222f18028a_64x64.jpg?v=1704619782"
                        },
                        "price": {
                            "amount": 629.95,
                            "currencyCode": "INR"
                        },
                        "product": {
                            "id": "8273463967958",
                            "title": "The Multi-managed Snowboard",
                            "vendor": "Multi-managed Vendor",
                            "type": "",
                            "untranslatedTitle": "The Multi-managed Snowboard",
                            "url": "/products/the-multi-managed-snowboard"
                        },
                        "sku": "sku-managed-1"
                    }
                },
                {
                    "discountAllocations": [],
                    "id": "44843038015702",
                    "quantity": 6,
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
                        }
                    }
                }
            ],
            "order": {},
            "shippingAddress": {
                "address1": "210, Lakshmi mega township, ragannaguda",
                "address2": "sss",
                "city": "Hyderabad1",
                "country": "IN",
                "countryCode": "IN",
                "firstName": "Swathi",
                "lastName": "Varkala",
                "phone": "",
                "province": "TS",
                "provinceCode": "TS",
                "zip": "501510"
            },
            "subtotalPrice": {
                "amount": 6389.55,
                "currencyCode": "INR"
            },
            "shippingLine": {
                "price": {
                    "amount": 0,
                    "currencyCode": "INR"
                }
            },
            "totalTax": {
                "amount": 1150.12,
                "currencyCode": "INR"
            },
            "totalPrice": {
                "amount": 7539.67,
                "currencyCode": "INR"
            },
            "transactions": []
        }
    },
    "clientId": "1fd529f6-8f05-4118-ba6b-a4e20691aa0c",
    "timestamp": "2024-01-16T09:27:44.342Z",
    "context": {
        "document": {
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtZMllEN0NZTkEwRVo3QlpHMkUyMEo4",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtZMllEN0NZTkEwRVo3QlpHMkUyMEo4",
                "port": "",
                "protocol": "https:",
                "search": ""
            },
            "referrer": "https://quickstart-6ebc0909.myshopify.com/products/the-collection-snowboard-liquid",
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
            "innerWidth": 487,
            "outerHeight": 775,
            "outerWidth": 1234,
            "pageXOffset": 0,
            "pageYOffset": 1090.5,
            "location": {
                "href": "https://quickstart-6ebc0909.myshopify.com/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtZMllEN0NZTkEwRVo3QlpHMkUyMEo4",
                "hash": "",
                "host": "quickstart-6ebc0909.myshopify.com",
                "hostname": "quickstart-6ebc0909.myshopify.com",
                "origin": "https://quickstart-6ebc0909.myshopify.com",
                "pathname": "/checkouts/cn/Z2NwLXVzLWNlbnRyYWwxOjAxSEtZMllEN0NZTkEwRVo3QlpHMkUyMEo4",
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
            "scrollY": 1090.5
        }
    }
};*/