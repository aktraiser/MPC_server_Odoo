#!/usr/bin/env python3
"""
Test script for the Odoo MCP HTTP API
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_connect():
    """Test connection to Odoo"""
    print("Testing connection to Odoo...")
    
    # Get credentials from environment or use test values
    payload = {
        "url": os.getenv("ODOO_URL", "https://demo.odoo.com"),
        "database": os.getenv("ODOO_DATABASE", "demo"),
        "username": os.getenv("ODOO_USERNAME", "demo"),
        "password": os.getenv("ODOO_PASSWORD", "demo")
    }
    
    response = requests.post(f"{BASE_URL}/connect", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.status_code == 200

def test_search():
    """Test searching records"""
    print("Testing search endpoint...")
    
    payload = {
        "model": "res.partner",
        "domain": [],
        "fields": ["name", "email"],
        "limit": 5
    }
    
    response = requests.post(f"{BASE_URL}/search", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_count():
    """Test counting records"""
    print("Testing count endpoint...")
    
    payload = {
        "model": "res.partner",
        "domain": []
    }
    
    response = requests.post(f"{BASE_URL}/count", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_models():
    """Test getting models"""
    print("Testing models endpoint...")
    
    payload = {
        "filter": "res"
    }
    
    response = requests.post(f"{BASE_URL}/models", json=payload)
    print(f"Status: {response.status_code}")
    # Don't print full response as it's too large
    data = response.json()
    if "models" in data:
        print(f"Found {data['count']} models matching 'res'")
        print(f"First 5: {data['models'][:5]}")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
    print()

def test_fields():
    """Test getting fields"""
    print("Testing fields endpoint...")
    
    payload = {
        "model": "res.partner"
    }
    
    response = requests.post(f"{BASE_URL}/fields", json=payload)
    print(f"Status: {response.status_code}")
    # Don't print full response as it's too large
    data = response.json()
    if "fields" in data:
        fields = list(data['fields'].keys())
        print(f"Found {len(fields)} fields for res.partner")
        print(f"First 10 fields: {fields[:10]}")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
    print()

def main():
    """Run all tests"""
    print("Starting Odoo MCP HTTP API tests...\n")
    
    # Test basic endpoints
    test_health()
    test_root()
    
    # Test connection
    connected = test_connect()
    
    if connected:
        # Test other endpoints only if connected
        test_search()
        test_count()
        test_models()
        test_fields()
    else:
        print("Connection failed. Skipping other tests.")
    
    print("\nTests completed!")

if __name__ == "__main__":
    main()