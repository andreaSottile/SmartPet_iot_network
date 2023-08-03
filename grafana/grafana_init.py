import requests
GRAFANA_API_KEY = 'grafana_api_key'
GRAFANA_SERVER_URL = 'http://serverurl'  # TODO

DJANGO_APP_NAME = 'Network_Controller'
DJANGO_API_ENDPOINTS = {
    # these URLs have been defined in urls.py
    'food': 'http://127.0.0.1:8000/api/real-time-food/',
    'heartbeat': 'http://127.0.0.1:8000/api/real-time-heartbeat/',
    'hatch': 'http://127.0.0.1:8000/api/real-time-hatch/',
    'live_clients': 'http://127.0.0.1:8000/api/real-time-live-clients/',
}


def create_grafana_data_source(url, request):
    global GRAFANA_SERVER_URL
    GRAFANA_SERVER_URL = "http://" + url

    # Set up the data source configuration for Grafana
    data_source_food = {
        "name": "Django Data Source",
        "type": "simple-json-datasource",
        "url": DJANGO_API_ENDPOINTS['food'],  # Using food API endpoint
        "jsonData": {  # TODO: JSON DI PROVA
            "timeField": "time",
            "valueField": "lvl"
        }
    }

    # Create the data source
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(DJANGO_API_ENDPOINTS['food'], json=data_source_food, headers=headers)

    if response.status_code == 200:
        print("Data source created successfully!")
    else:
        print("Failed to create data source:", response.json())


def create_grafana_dashboard(request):
    # TODO: Grafana JSON here
    dashboard = {
        # dashboard JSON
    }

    # Create the dashboard
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(DJANGO_API_ENDPOINTS['food'], json={"dashboard": dashboard}, headers=headers)

    if response.status_code == 200:
        print("Dashboard created successfully!")
    else:
        print("Failed to create dashboard:", response.json())
