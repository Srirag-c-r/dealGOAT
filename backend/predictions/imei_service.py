
"""
Service to handle IMEI lookups.
Integrates with RapidAPI (Kelpom IMEI Checker) for real data.
Falls back to mock data if API key is missing or request fails.
"""

"""
Service to handle IMEI lookups.
RELIABLE IMPLEMENTATION:
1. Checks for Real API Key (RapidAPI).
2. If available, tries to fetch real data.
3. If not available or fails, falls back to MOCK data for demonstration.
"""
import requests
from decouple import config

def get_real_specs(imei, api_key):
    """
    Fetch device specs from RapidAPI (Kelpom or compatible IMEI Checker).
    Using a generic endpoint that often works with Kelpom or equivalent.
    """
    # The endpoint below is for 'Kelpom IMEI Checker' on RapidAPI.
    # If the user subscribed to a different one, they might need to change this URL.
    url = "https://kelpom-imei-checker1.p.rapidapi.com/api/v1/imei-checker"
    
    querystring = {"imei": imei}

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "kelpom-imei-checker1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                info = data.get('object', {})
                return {
                    'brand': info.get('brand', 'Unknown'),
                    'model': info.get('model', 'Unknown'),
                    'launch_year': 2023, # API often doesn't give this, defaulting
                    'processor': 'Unknown',
                    'storage_gb': 128,
                    'ram_gb': 8,
                    'battery_percentage': 100,
                    'battery_health': 100,
                    'condition': 'Good',
                    'supports_5g': True
                }
    except Exception as e:
        print(f"API Lookup Failed: {e}")
        return None
    return None

def get_mock_specs(imei):
    """
    Reliable Offline/Demo Data.
    Works 100% of the time for specific test IMEIs.
    """
    mock_db = {
        # iPhone 14
        '354890123456789': {
            'brand': 'Apple',
            'model': 'iPhone 14',
            'launch_year': 2022,
            'launch_price': 79900,
            'processor': 'Apple A15 Bionic',
            'storage_gb': 128,
            'ram_gb': 6,
            'battery_percentage': 100, 
            'battery_health': 100,
            'camera_rear_mp': 12,
            'camera_front_mp': 12,
            'display_type': 'OLED',
            'display_size_inch': 6.1,
            'supports_5g': True,
        },
        # Samsung S23
        '865432109876543': {
            'brand': 'Samsung',
            'model': 'Galaxy S23',
            'launch_year': 2023,
            'launch_price': 74999,
            'processor': 'Snapdragon 8 Gen 2',
            'storage_gb': 256,
            'ram_gb': 8,
            'battery_percentage': 100,
            'battery_health': 100,
            'camera_rear_mp': 50,
            'camera_front_mp': 12,
            'display_type': 'AMOLED',
            'display_size_inch': 6.1,
            'supports_5g': True,
        },
        # OnePlus 11R
        '990011223344556': {
            'brand': 'OnePlus',
            'model': '11R',
            'launch_year': 2023,
            'launch_price': 39999,
            'processor': 'Snapdragon 8+ Gen 1',
            'storage_gb': 256,
            'ram_gb': 16,
            'battery_percentage': 100,
            'battery_health': 100,
            'camera_rear_mp': 50,
            'camera_front_mp': 16,
            'display_type': 'AMOLED',
            'display_size_inch': 6.7,
            'supports_5g': True,
        }
    }
    return mock_db.get(str(imei))

def get_specs_from_imei(imei):
    """
    Main Entry Point.
    Strategy:
    1. Check for API Key -> Try Real API.
    2. If fails/no key -> Check Mock DB.
    3. If not in Mock DB -> Return None (Manual Entry).
    """
    # 1. Try Real API if configured
    api_key = config('RAPIDAPI_KEY', default=None)
    if api_key:
        print(f"Attempting Real API lookup for {imei}...")
        specs = get_real_specs(imei, api_key)
        if specs:
            return specs
            
    # 2. Fallback to Mock
    print(f"Falling back to Mock lookup for {imei}...")
    return get_mock_specs(imei)
