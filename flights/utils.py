import requests
from decouple import config

def get_flights(from_city, to_city, travel_date):
    access_key = config('flight_access_key')
    
    try:
        print(f"Requesting flights from {from_city} to {to_city} on {travel_date}")
        
        url = f"http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": access_key,
            "dep_iata": from_city,  
            "arr_iata": to_city,    
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error fetching flights: {response.text}")
        
        data = response.json()
        flights = data.get("data", [])
        filtered_flights = [flight for flight in flights if flight['departure']['scheduled'].startswith(travel_date)]
        if not filtered_flights:
            print("No filtered_flights found for")
            return(f"No flights found for {from_city} to {to_city} on {travel_date}")
        # print("filtered_flights",filtered_flights)

        return filtered_flights
    
    except Exception as e:
        print(f"Error during flight request: {e}")
        raise Exception(f"Error fetching flights: {e}")
