import base64
import requests
import xml.etree.ElementTree as ET
import os
import subprocess
import wmi
import hashlib
import csv

def base64_encode(string):
    return base64.b64encode(string.encode()).decode()

def get_device_token():
    c = wmi.WMI()
    concat = ''

    queries = [
        "SELECT * FROM Win32_BaseBoard",
        "SELECT * FROM Win32_BIOS",
        "SELECT * FROM Win32_OperatingSystem"
    ]

    for query in queries:
        for obj in c.query(query):
            serial_number = obj.SerialNumber
            if serial_number:
                concat += serial_number

    return hashlib.sha1(concat.encode()).hexdigest()

def generate_access_token(email, password, client_token):
    data = {
        "guid": email,
        "password": password,
        "clientToken": client_token,
        "game_net": "Unity",
        "play_platform": "Unity",
        "game_net_user_id": ""
    }
    try:
        url = "https://www.realmofthemadgod.com/account/verify"
        verify_request = requests.post(url, data=data, headers=headers)
        verify_request_data = verify_request.content
        access_token = ET.fromstring(verify_request_data).find(".//AccessToken").text
        timestamp = ET.fromstring(verify_request_data).find(".//AccessTokenTimestamp").text
        if access_token and timestamp:
            print("[SUCCESS] AccessToken:", access_token)
            print("[SUCCESS] Timestamp:", timestamp)
            return access_token, timestamp
    except Exception as e:
        print("[FAILURE] Failed to generate AccessToken & Timestamp -", e)

def start_instance(accounts):
    default_exe = f"C:/Users/{os.getlogin()}/Documents/RealmOfTheMadGod/Production/RotMG Exalt.exe"
    email = accounts["email"]
    password = accounts["password"]
    username = accounts["username"]
    nickname = accounts["nickname"]

    client_token = get_device_token()
    access_token, timestamp = generate_access_token(email, password, client_token)

    exe_path = os.getenv('ROTMG_PATH', default_exe)
    data = f"data:{{platform:Deca,guid:{base64_encode(email)},token:{base64_encode(access_token)},tokenTimestamp:{base64_encode(timestamp)},tokenExpiration:MTMwMDAwMA==,env:4}}"
    
    os.chdir(os.path.dirname(exe_path))
    subprocess.Popen([exe_path, data, f"-screen-width","800", f"-screen-height", "600", "-screen-fullscreen", "0"])
    
    print(f"Started instance for [{nickname}] {username} - ({email})")

def main():
    with open("accounts.csv", "r") as file:
        accounts = csv.DictReader(file)
        accounts = [dict(account) for account in accounts]

    print("Accounts:")
    for index, account in enumerate(accounts, start=1):
        email = account["email"]
        username = account["username"]
        nickname = account["nickname"]
        print(f"{index}. [{nickname}] {username} | {email}")

    while True:
        try:
            user_input = int(input(f"Select an account by index to start an instance (or enter 0 to exit): "))
            if user_input == 0:
                break
            elif 1 <= user_input <= len(accounts):
                start_instance(accounts[user_input - 1])
            else:
                raise ValueError
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

if __name__ == "__main__":
    headers = {
            "User-Agent": "UnityPlayer/2021.3.5f1 (UnityWebRequest/1.0, libcurl/7.80.0-DEV)",
            "Accept": "*/*",
            "Accept-Encoding": "deflate, gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2021.3.5f1"
        }
    
    main()