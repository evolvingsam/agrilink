import math
import json
import logging
import requests
from django.conf import settings
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from .models import DispatchRoute
from matching.models import Match

logger = logging.getLogger(__name__)

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    """
    if None in (lat1, lon1, lat2, lon2):
        return 0.0

    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [float(lon1), float(lat1), float(lon2), float(lat2)])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

def create_data_model(matches):
    """Stores the data for the routing problem."""
    data = {}
    
    # Node 0 is a virtual depot (could be dispatcher's starting location)
    # We will just use the first collection point as a mock depot for MVP
    locations = [{'name': 'Depot', 'lat': 0.0, 'lng': 0.0}] 
    
    if matches:
        first_cp = matches[0].listing.collection_point
        if first_cp:
            locations[0] = {'name': f"Depot ({first_cp.name})", 'lat': float(first_cp.latitude or 0), 'lng': float(first_cp.longitude or 0)}

    # Add pickup (collection point) and delivery (buyer location) for each match
    # A single match requires visiting pickup, then delivery
    pickups_deliveries = []
    
    current_index = 1
    for match in matches:
        cp = match.listing.collection_point
        buyer = match.order.buyer.buyer_profile
        
        pickup_lat, pickup_lng = float(cp.latitude or 0), float(cp.longitude or 0)
        delivery_lat, delivery_lng = float(buyer.latitude or 0), float(buyer.longitude or 0)
        
        locations.append({'name': f"Pickup: {cp.name} (Match {match.id})", 'lat': pickup_lat, 'lng': pickup_lng, 'type': 'pickup', 'match_id': match.id})
        pickup_idx = current_index
        current_index += 1
        
        locations.append({'name': f"Delivery: {buyer.business_name or buyer.user.username} (Match {match.id})", 'lat': delivery_lat, 'lng': delivery_lng, 'type': 'delivery', 'match_id': match.id})
        delivery_idx = current_index
        current_index += 1
        
        pickups_deliveries.append([pickup_idx, delivery_idx])
        
    data['locations'] = locations
    
    # Build distance matrix
    distance_matrix = []
    for i in range(len(locations)):
        row = []
        for j in range(len(locations)):
            dist = haversine(locations[i]['lat'], locations[i]['lng'], locations[j]['lat'], locations[j]['lng'])
            # OR-Tools requires integer distances. Multiply by 1000 to get meters.
            row.append(int(dist * 1000))
        distance_matrix.append(row)
        
    data['distance_matrix'] = distance_matrix
    data['pickups_deliveries'] = pickups_deliveries
    data['num_vehicles'] = 1 # Single truck for MVP
    data['depot'] = 0
    return data

def generate_routes() -> int:
    """Finds optimal routes for pending matches using OR-Tools."""
    matches = list(Match.objects.filter(status=Match.Status.PENDING_DELIVERY, routes__isnull=True))
    if not matches:
        return 0

    data = create_data_model(matches)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        # Returns the distance between the two nodes.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000000,  # vehicle maximum travel distance (meters) - 3000km
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Define Transportation Requests.
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_index) <=
            distance_dimension.CumulVar(delivery_index))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        # Extract route
        index = routing.Start(0)
        route_waypoints = []
        route_distance = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            loc = data['locations'][node_index]
            route_waypoints.append(loc)
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, 0)

        # Add depot at end
        node_index = manager.IndexToNode(index)
        route_waypoints.append(data['locations'][node_index])
        
        distance_km = route_distance / 1000.0

        route = DispatchRoute.objects.create(
            route_waypoints=route_waypoints,
            estimated_distance_km=distance_km,
            status=DispatchRoute.Status.PLANNED
        )
        route.matches.set(matches)

        # Generate briefing
        route.briefing_text = generate_briefing(route)
        route.save(update_fields=['briefing_text'])

        return 1
    else:
        logger.error('No solution found for routing!')
        return 0

def generate_briefing(route: DispatchRoute) -> str:
    """Uses Gemma 4 to generate a natural language briefing for the route."""
    api_key = getattr(settings, 'GOOGLE_AI_API_KEY', None)
    if not api_key:
        return "Mock briefing: Pick up from locations and deliver to buyers as per waypoints."

    # Prepare waypoints for prompt
    waypoints_text = "\n".join([f"- {i+1}. {wp['name']}" for i, wp in enumerate(route.route_waypoints)])

    prompt = f"""You are the AgriLink Dispatch Coordinator.
Translate this mathematical route plan into a friendly, clear, natural language briefing for our truck driver.
Tell them exactly where to go first, where to pick up, and where to deliver. 
Make it sound like human instructions (e.g., "First, head over to the Depot to start...").

Route Waypoints:
{waypoints_text}

Estimated Total Distance: {route.estimated_distance_km} km.

Keep it concise and clear."""

    use_openrouter = api_key.startswith('sk-or-v1')
    
    if use_openrouter:
        url = 'https://openrouter.ai/api/v1/chat/completions'
        model = settings.GOOGLE_AI_MODEL if settings.GOOGLE_AI_MODEL != 'gemma-3-27b-it' else 'google/gemma-4-31b-it'
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.4,
            'max_tokens': 300,
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Gemma 4 briefing error: {e}")
            return "Failed to generate briefing."
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GOOGLE_AI_MODEL}:generateContent?key={api_key}"
        payload = {
            'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': 0.4,
                'maxOutputTokens': 300,
            },
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error(f"Gemma 4 briefing error: {e}")
            return "Failed to generate briefing."
