"""
Weather Forecasting Application
Main entry point for the application
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
            return jsonify({"status": "error", "message": "City not found"}), 404
    except Exception as e:
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
            return jsonify([])
    except Exception as e:
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
            return jsonify({"status": "error", "message": "Weather data not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/weather", methods=["GET", "POST"])
def weather():
    """Serve weather page"""
    # For GET requests, just serve the template
    # The template will fetch data via JavaScript using URL parameters
    if request.method == "GET":
        return render_template("weather.html")
    
    # Legacy POST endpoint - redirects to new API
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
            return "City not found!", 404
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":

    debug = os.getenv("DEBUG", "False") == "True"
    port = int(os.getenv("PORT", "8000"))

    print("Weather Forecasting Application")
    print("================================")
    print(f"Debug Mode: {debug}")
    print(f"Port: {port}")

    app.run(debug=debug, port=port)