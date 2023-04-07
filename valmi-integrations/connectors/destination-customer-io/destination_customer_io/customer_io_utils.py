import requests


def get_region(site_id: str, tracking_api_key: str):
    headers = {"Authorization": f"Basic {site_id}:{tracking_api_key}"}

    conn = requests.get("https://track.customer.io/api/v1/accounts/region", headers=headers)
    if conn.text is None:
        raise Exception("Could not get region with provided credentials")
    return conn.text
