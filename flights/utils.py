# from amadeus import Client, ResponseError

# amadeus = Client(client_id='TzDkIoSBg3I1uRr2fHBwDcwPcEYMcfzv',client_secret='XgIADv3Q1KkZlNLp')

# def get_flights(from_city, to_city, travel_date):
#     try:
#         response = amadeus.shopping.flight_offers_search.get(
#             originLocationCode=from_city,
#             destinationLocationCode=to_city,
#             departureDate=travel_date,
#             adults=1
#         )
#         # Process and return the flight data
#         flights = response.data 
#         flights = response.data[:15]
#         return flights
#     except ResponseError as e:
#         raise Exception(f"Error fetching flights: {e}")



import requests

def get_flights(from_city, to_city, travel_date):
    access_key = "513dd9ebdb2690c720f4b644eae3fbe4"  
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
