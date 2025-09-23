#!/usr/bin/env python3

import os
import asyncio
import requests
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv('/app/backend/.env')

async def setup_test_user():
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'dhruv_ai_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test user credentials
        test_email = "test@dhruvai.com"
        test_password = "password123"
        
        # Check if test user already exists
        existing_user = await db.users.find_one({"email": test_email})
        
        if existing_user:
            print(f"Test user {test_email} already exists")
            client.close()
            return test_email, test_password
        
        # Create test user
        password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_data = {
            "user_id": str(uuid.uuid4()),
            "full_name": "Test User",
            "email": test_email,
            "password_hash": password_hash,
            "exam_type": "JEE",
            "grade": "12th",
            "target_year": 2025,
            "parent_email": None,
            "subscription_type": "free",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        await db.users.insert_one(user_data)
        print(f"Created test user: {test_email}")
        
        client.close()
        return test_email, test_password
        
    except Exception as e:
        print(f"Error setting up test user: {e}")
        return None, None

def test_login(email, password):
    try:
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        
        print(f"Testing login at {backend_url}/api/auth/login")
        print(f"Credentials: {email} / {password}")
        
        response = requests.post(f"{backend_url}/api/auth/login", json={
            "email": email,
            "password": password
        }, timeout=10)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Login successful!")
            print(f"Token received: {data.get('token', 'No token')[:50]}...")
            return data.get('token')
        else:
            print(f"Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"Login test error: {e}")
        return None

def test_mock_generation(token):
    try:
        backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        
        print(f"\nTesting mock test generation...")
        
        response = requests.post(f"{backend_url}/api/mock-tests/generate", 
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={
                "exam_type": "JEE",
                "subject": "Mathematics", 
                "difficulty": 3,
                "num_questions": 5
            },
            timeout=30
        )
        
        print(f"Mock test response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Mock test generation successful!")
            print(f"Test ID: {data.get('test_id')}")
            print(f"Questions generated: {len(data.get('questions', []))}")
            if data.get('questions'):
                print(f"Sample question: {data['questions'][0]['question_text'][:100]}...")
            return True
        else:
            print(f"Mock test generation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Mock test generation error: {e}")
        return False

async def main():
    print("Setting up test environment...")
    
    # Setup test user
    email, password = await setup_test_user()
    if not email:
        print("Failed to setup test user")
        return
    
    # Test login
    token = test_login(email, password)
    if not token:
        print("Authentication test failed")
        return
    
    # Test mock test generation
    mock_success = test_mock_generation(token)
    
    if mock_success:
        print("\n✅ All tests passed! Authentication and mock test generation working correctly.")
        print(f"\nTest credentials for frontend testing:")
        print(f"Email: {email}")
        print(f"Password: {password}")
    else:
        print("\n❌ Mock test generation failed")

if __name__ == "__main__":
    asyncio.run(main())