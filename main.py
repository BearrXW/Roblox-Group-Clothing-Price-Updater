import requests
import json
import time
from termcolor import colored

# Function to check the request status
def check_request(action, method, response):
    if response.status_code != 200:
        if response.status_code == 429:  # Rate limit status code
            print(colored(f"Rate limited: Waiting for 30 seconds", "yellow"))
            time.sleep(30)
        else:
            raise Exception(colored(f"{action} {method} request failed: {response.status_code} - {response.text}", "red"))

# Function to read configuration from config.json
def read_config(filename):
    with open(filename, "r") as f:
        config = json.load(f)
    return config

# Function to get all clothing items in the group
def get_group_clothing(group_id, limit, cookie):
    url = f"https://catalog.roblox.com/v1/search/items/details?Category=3&CreatorType=2&IncludeNotForSale=true&Limit={limit}&CreatorTargetId={group_id}"
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}"
    }
    all_items = []
    cursor = ""
    while True:
        if cursor:
            url_with_cursor = f"{url}&Cursor={cursor}"
        else:
            url_with_cursor = url
        response = requests.get(url_with_cursor, headers=headers)
        check_request("GET-CLOTHING", "GET", response)
        data = response.json()
        all_items.extend(data["data"])
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return all_items

# Function to update the price of a clothing item
def update_clothing_price(asset_id, amount, csrf_token, cookie):
    url = f"https://itemconfiguration.roblox.com/v1/assets/{asset_id}/update-price"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f".ROBLOSECURITY={cookie}",
        "X-CSRF-TOKEN": csrf_token
    }
    data = json.dumps({"priceConfiguration": {"priceInRobux": str(amount)}})
    response = requests.post(url, headers=headers, data=data)
    check_request("UPDATE-PRICE", "POST", response)
    print(colored(f"Updated item {asset_id} to price {amount} Robux", "green"))
    time.sleep(10)  # Wait for 10 seconds before next request

# Function to get CSRF token
def get_csrf_token(cookie):
    url = "https://itemconfiguration.roblox.com/v1/assets/1/update-price"  # Dummy request to get the token
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 403:
        return response.headers["x-csrf-token"]
    check_request("GET-CSRF-TOKEN", "POST", response)

# Main script
def main():
    try:
        config = read_config("config.json")
        cookie = config["COOKIE"]
        group_id = config["GROUP_ID"]
        new_price = config["NEW_PRICE"]
        limit = config["LIMIT"]

        csrf_token = get_csrf_token(cookie)
        clothing_items = get_group_clothing(group_id, limit, cookie)
        print(colored(f"Fetching {len(clothing_items)} clothing items from group {group_id}...", "cyan"))
        
        for item in clothing_items:
            asset_id = item["id"]
            try:
                update_clothing_price(asset_id, new_price, csrf_token, cookie)
            except Exception as e:
                print(colored(f"Failed to update price for item {asset_id}: {e}", "red"))
        
        print(colored(f"Successfully updated prices for all items in group {group_id}!", "green"))
    except Exception as e:
        print(colored(f"Error: {e}", "red"))



if __name__ == "__main__":
    print(colored("Starting Roblox Group Clothing Price Updater...", "blue"))
    main()
