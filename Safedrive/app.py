import requests
import json
import time

TOMTOM_API_KEY = ''
IPINFO_TOKEN = '' 

def get_current_location():
    response = requests.get(f'https://ipinfo.io?token={IPINFO_TOKEN}')
    if response.status_code == 200:
        data = response.json()
        if 'loc' in data:
            latitude, longitude = map(float, data['loc'].split(','))
            return latitude, longitude
    return None

def get_traffic_data(latitude, longitude):
    url = f'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json?point={latitude},{longitude}&unit=KMPH&openLr=false&&key={TOMTOM_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        traffic_data = response.json()
        return traffic_data
    else:
        print(f"Error: {response.status_code}")
        return None

def save_traffic_data_to_file(traffic_data):
    with open('traffic_data.json', 'w') as file:
        json.dump(traffic_data, file, indent=4)

def main():
    while True:
        coordinates = get_current_location()
        if coordinates:
            latitude, longitude = coordinates
            print(f"Current Location: Latitude {latitude}, Longitude {longitude}")
            
            traffic_data = get_traffic_data(latitude, longitude)
            
            if traffic_data:
                print("Traffic Data:")
                print(json.dumps(traffic_data, indent=4))
                save_traffic_data_to_file(traffic_data)
        else:
            print("Unable to retrieve current location.")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
