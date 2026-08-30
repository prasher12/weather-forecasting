"""
Weather Forecasting Application
Main entry point for the application with Render live deployment diagnostics
"""

import os
import requests
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Create Flask application
app = Flask(__name__)

# Get API key
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# --- RENDER DEPLOYMENT DIAGNOSTICS ---
# This prints to your Render logs on startup so you know if your key loaded correctly
print("==================================================")
print("RENDER LIVE ENVIRONMENT DIAGNOSTICS")
if not API_KEY:
    print("❌ ERROR: 'OPENWEATHER_API_KEY' was not found in environment variables!")
    print("👉 ACTION REQUIRED: Go to your Render Environment tab and add 'OPENWEATHER_API_KEY'")
else:
    # Safely print a masked version of the key to verify it exists without revealing it in logs
    masked_key = API_KEY[:4] + "..." + API_KEY[-4:] if len(API_KEY) > 8 else "Loaded (Too Short)"
    print(f"✅ SUCCESS: 'OPENWEATHER_API_KEY' loaded successfully. (Value: {masked_key})")
print("==================================================")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/weather/<city>")
def get_weather(city):
    """Get current weather data for a city"""
    try:
        # Current weather
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(weather_url, params=params)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            # Get forecast data (5-day, 3-hour)
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_response = requests.get(forecast_url, params=params)
            forecast_data = forecast_response.json() if forecast_response.status_code == 200 else {}
            
            return jsonify({
                "weather": weather_data,
                "forecast": forecast_data,
                "status": "success"
            })
        else:
            print(f"❌ WEATHER API ERROR FOR CITY '{city}': Status Code {response.status_code}")
            print(f"   Response Text: {response.text}")
            return jsonify({"status": "error", "message": "City not found"}), 404
    except Exception as e:
        print(f"💥 WEATHER API EXCEPTION: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/autocomplete")
def autocomplete():
    """Get city suggestions for autocomplete"""
    query = request.args.get("q", "").strip()
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        # Using geolocation API to get city suggestions
        geo_url = "https://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": query,
            "limit": 5,
            "appid": API_KEY
        }
        response = requests.get(geo_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            suggestions = [
                {
                    "name": city["name"],
                    "country": city.get("country", ""),
                    "state": city.get("state", ""),
                    "lat": city["lat"],
                    "lon": city["lon"]
                }
                for city in data
            ]
            return jsonify(suggestions)
        else:
            print(f"❌ AUTOCOMPLETE API ERROR FOR QUERY '{query}': Status Code {response.status_code}")
            print(f"   Response Text: {response.text}")
            return jsonify([])
    except Exception as e:
        print(f"💥 AUTOCOMPLETE API EXCEPTION: {str(e)}")
        return jsonify([])


@app.route("/api/weather-by-coords")
def weather_by_coords():
    """Get weather by latitude and longitude"""
    try:
        lat = request.args.get("lat")
        lon = request.args.get("lon")
        
        if not lat or not lon:
            return jsonify({"status": "error", "message": "Missing coordinates"}), 400
        
        # Current weather
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(weather_url, params=params)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            # Get forecast data
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_response = requests.get(forecast_url, params=params)
            forecast_data = forecast_response.json() if forecast_response.status_code == 200 else {}
            
            return jsonify({
                "weather": weather_data,
                "forecast": forecast_data,
                "status": "success"
            })
        else:
            print(f"❌ COORDS API ERROR (lat: {lat}, lon: {lon}): Status Code {response.status_code}")
            print(f"   Response Text: {response.text}")
            return jsonify({"status": "error", "message": "Weather data not found"}), 404
    except Exception as e:
        print(f"💥 COORDS API EXCEPTION: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/weather", methods=["GET", "POST"])
def weather():
    """Serve weather page"""
    if request.method == "GET":
        return render_template("weather.html")
    
    city = request.form.get("city")
    
    if not city:
        return "City name required!", 400
    
    try:
        # Current weather
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(weather_url, params=params)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            # Get forecast data
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            forecast_response = requests.get(forecast_url, params=params)
            forecast_data = forecast_response.json() if forecast_response.status_code == 200 else {}
            
            return render_template(
                "weather.html",
                data=weather_data,
                forecast=forecast_data
            )
        else:
            print(f"❌ LEGACY WEATHER PAGE ERROR FOR '{city}': Status Code {response.status_code}")
            print(f"   Response Text: {response.text}")
            return "City not found!", 404
    except Exception as e:
        print(f"💥 LEGACY WEATHER PAGE EXCEPTION: {str(e)}")
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    debug = os.getenv("DEBUG", "False") == "True"
    port = int(os.getenv("PORT", "8000"))

    print("Weather Forecasting Application")
    print("================================")
    print(f"Debug Mode: {debug}")
    print(f"Port: {port}")

    app.run(debug=debug, port=port)
