import datetime as dt
import requests
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = ""
CITY = "Chennai"

def kelvin_to_celsius_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit

def get_weather():
    url = f"{BASE_URL}q={CITY}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            weather_main = data['weather'][0]['main']
            temp_kelvin = data['main']['temp']
            temp_celsius, temp_fahrenheit = kelvin_to_celsius_fahrenheit(temp_kelvin)
            feels_like_kelvin = data['main']['feels_like']
            feels_like_celsius, feels_like_fahrenheit = kelvin_to_celsius_fahrenheit(feels_like_kelvin)
            wind_speed = data['wind']['speed']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            sunrise_time = dt.datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
            sunset_time = dt.datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

            return {
                "weather_main": weather_main,
                "temperature": f"{temp_celsius:.2f} / {temp_fahrenheit:.2f}",
                "feels_like": f"{feels_like_celsius:.2f}°C / {feels_like_fahrenheit:.2f}°F",
                "humidity": f"{humidity}%",
                "wind_speed": f"{wind_speed}m/s",
                "description": description,
                "sunrise_time": sunrise_time.strftime("%Y-%m-%d %H:%M:%S"),
                "sunset_time": sunset_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except KeyError as e:
            print(f"Error: Missing key in weather data: {e}")
            return None
    else:
        print(f"Error: Failed to fetch weather data. Status code: {response.status_code}")
        return None

def classify_intent(user_input):
    user_input = user_input.lower()
    if 'weather' in user_input:
        return 'weather'
    elif 'temperature' in user_input:
        return 'temperature'
    elif 'wind' in user_input:
        return 'wind'
    elif 'humidity' in user_input:
        return 'humidity'
    elif 'climate' in user_input or 'today' in user_input:
        return 'climate'
    elif 'exit' in user_input or 'quit' in user_input or 'bye' in user_input:
        return 'exit'
    else:
        return 'unknown'

def analyze_climate(weather_main, temp_celsius):
    if weather_main.lower() in ['clear', 'clouds']:
        if temp_celsius > 25:
            return "Hot"
        elif temp_celsius < 15:
            return "Cool"
        else:
            return "Moderate"
    elif weather_main.lower() in ['rain', 'drizzle']:
        return "Rainy"
    elif weather_main.lower() in ['thunderstorm']:
        return "Stormy"
    elif weather_main.lower() in ['snow']:
        return "Snowy"
    else:
        return "Unknown"
    
def generate_weather_image(weather_data):
    
    image = Image.new("RGB", (400, 200), "white")
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    draw.text((10, 10), f"Weather: {weather_data['weather_main']}", fill="black", font=font)
    draw.text((10, 40), f"Description: {weather_data['description']}", fill="black", font=font)
    draw.text((10, 70), f"Temperature: {weather_data['temperature']}", fill="black", font=font)
    draw.text((10, 100), f"Humidity: {weather_data['humidity']}", fill="black", font=font)
    draw.text((10, 130), f"Wind Speed: {weather_data['wind_speed']}", fill="black", font=font)
    draw.text((10, 160), f"Sunrise Time: {weather_data['sunrise_time']}", fill="black", font=font)
    draw.text((10, 190), f"Sunset Time: {weather_data['sunset_time']}", fill="black", font=font)

    image.save("weather_image.png")
    image.show()
 

def chat_bot():
    print("Hello! I am Weather Bot. How can I assist you today?")
    while True:
        user_input = input("You: ").strip()
        intent = classify_intent(user_input)
        if intent == 'exit':
            print("Weather Bot: Goodbye! Have a nice day.")
            break
        elif 'weather' in intent or 'climate' in intent:
            weather_data = get_weather()
            if weather_data:
                print(f"Weather Bot: The weather in {CITY} is {weather_data['weather_main'].lower()}.")
                print(f"Description: {weather_data['description']}")
                print(f"Temperature: {weather_data['temperature']}")
                print(f"Humidity: {weather_data['humidity']}")
                print(f"Wind Speed: {weather_data['wind_speed']}")
                print(f"Sunrise Time: {weather_data['sunrise_time']}")
                print(f"Sunset Time: {weather_data['sunset_time']}")
                generate_weather_image(weather_data)
            else:
                print("Weather Bot: Sorry, unable to fetch weather information.")
        elif intent in ['temperature', 'wind', 'humidity']:
            weather_data = get_weather()
            if weather_data:
                print(f"Weather Bot: The {intent} in {CITY} is {weather_data[intent]}.")
            else:
                print("Weather Bot: Sorry, unable to fetch weather information.")
        elif intent == 'unknown':
            print("Weather Bot: Sorry, I didn't understand. You can ask me about the weather, temperature, wind, humidity, or climate.")
        else:
            print("Weather Bot: Sorry, something went wrong. Please try again.")

if __name__ == "__main__":
    chat_bot()
