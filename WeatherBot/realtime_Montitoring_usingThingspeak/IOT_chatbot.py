import requests
from io import BytesIO


def get_weather_data():
    url = "https://api.thingspeak.com/channels/2198973/feeds.json?api_key=&results=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'feeds' in data and data['feeds']:
            return data['feeds'][0] 
        else:
            print("No data available in the response.")
    else:
        print(f"Failed to retrieve data from ThingSpeak. Status code: {response.status_code}")

    return None


def process_weather_data(weather_data):
    temperature = float(weather_data['field1'])
    humidity = float(weather_data['field2'])
    pressure = float(weather_data['field3'])
    rainfall = int(weather_data['field4'])
    return temperature, humidity, pressure, rainfall


def generate_response(query, weather_data):
    temperature, humidity, pressure, rainfall = process_weather_data(weather_data)
    
   
    if "temperature" in query:
        return f"The current temperature is {temperature} degrees Celsius."
    elif "humidity" in query:
        return f"The current humidity is {humidity}%."
    elif "pressure" in query:
        return f"The current pressure is {pressure} mb."
    elif "rainfall" in query:
        return f"The current rainfall is {rainfall}%."
    else:
        return "I'm sorry, I couldn't understand your question."


def generate_weather_image(weather_data):
    temperature, humidity, pressure, rainfall = process_weather_data(weather_data)
    
   
    prompt = f"Weather: Temperature {temperature}°C, Humidity {humidity}%, Pressure {pressure}mb, Rainfall {rainfall}%"
    
    
    response = requests.post(
        "https://api.openai.com/v1/images", 
        headers={"Authorization": "Bearer YOUR_API_KEY"}, 
        json={"prompt": prompt}
    )
    
    
# Main function
def main():
    while True:
        query = input("Ask me about the weather: ")
        
        # Retrieve weather data from ThingSpeak
        weather_data = get_weather_data()
        
        # Generate response based on user query and weather data
        response = generate_response(query.lower(), weather_data)
        print(response)
        

# Run the main function
if __name__ == "__main__":
    main()


