import requests
import subprocess

# TODO:
GRAFANA_API_KEY = 'grafana_api_key'
GRAFANA_SERVER_URL = 'http://serverurl'

DJANGO_APP_NAME = 'Network_Controller'
DJANGO_API_ENDPOINTS = {
    'food': 'http://127.0.0.1:8000/api/real-time-food/',
    'heartbeat': 'http://127.0.0.1:8000/api/real-time-heartbeat/',
    'hatch': 'http://127.0.0.1:8000/api/real-time-hatch/',
    'live_clients': 'http://127.0.0.1:8000/api/real-time-live-clients/',
}


def create_grafana_data_source():
    # Set up the data source configuration for Grafana
    data_source = {
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
    response = requests.post(f"{GRAFANA_SERVER_URL}/api/datasources", json=data_source, headers=headers)

    if response.status_code == 200:
        print("Data source created successfully!")
    else:
        print("Failed to create data source:", response.json())


def create_grafana_dashboard():
    # TODO: Grafana JSON here
    dashboard = {
        # dashboard JSON
    }

    # Create the dashboard
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{GRAFANA_SERVER_URL}/api/dashboards/db", json={"dashboard": dashboard}, headers=headers)

    if response.status_code == 200:
        print("Dashboard created successfully!")
    else:
        print("Failed to create dashboard:", response.json())


def setup_django_app():
    # Run Django management commands to set up the application
    subprocess.run(["python", f"{DJANGO_APP_NAME}/manage.py", "makemigrations"])
    subprocess.run(["python", f"{DJANGO_APP_NAME}/manage.py", "migrate"])


if __name__ == "__main__":
    # Create Grafana data source and dashboard
    create_grafana_data_source()
    create_grafana_dashboard()

    # Invoke Django setup function
    setup_django_app()
