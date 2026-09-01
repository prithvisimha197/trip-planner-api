#!/bin/bash

# Simple API test script

API_URL="http://localhost:5000"

echo "🧪 Testing Trip Planner API..."
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
curl -s $API_URL/health | jq .
echo ""

# Test 2: Register user
echo "2️⃣ Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST $API_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "dob": "1995-05-15",
    "securityQuestion": "firstConcert",
    "securityAnswer": "Beatles"
  }')
echo $REGISTER_RESPONSE | jq .
echo ""

# Test 3: Login
echo "3️⃣ Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }')
echo $LOGIN_RESPONSE | jq .

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token')
echo "Token: $TOKEN"
echo ""

# Test 4: Create trip
echo "4️⃣ Creating a trip..."
TRIP_RESPONSE=$(curl -s -X POST $API_URL/api/trips \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Trip to Tokyo",
    "destination": "Tokyo, Japan",
    "startDate": "2026-10-01",
    "endDate": "2026-10-07"
  }')
echo $TRIP_RESPONSE | jq .

TRIP_ID=$(echo $TRIP_RESPONSE | jq -r '.id')
echo ""

# Test 5: Get all trips
echo "5️⃣ Getting all trips..."
curl -s -X GET $API_URL/api/trips \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

# Test 6: Add place to trip
echo "6️⃣ Adding a place to trip..."
curl -s -X POST $API_URL/api/trips/$TRIP_ID/places \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Visit Tokyo Tower"
  }' | jq .
echo ""

# Test 7: Get trip details
echo "7️⃣ Getting trip details..."
curl -s -X GET $API_URL/api/trips/$TRIP_ID \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

echo "✅ API tests complete!"
