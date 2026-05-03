#!/bin/bash

# Comprehensive debugging script for data generation and API health

echo "═══════════════════════════════════════════════════════════"
echo "🔍 Azure Cost Simulator - Debug & Data Generation"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Step 1: Check backend running
echo ""
echo "📋 Step 1: Checking backend status..."
BACKEND_RUNNING=$(docker ps | grep fastapi-backend | wc -l)

if [ $BACKEND_RUNNING -gt 0 ]; then
    print_status 0 "Backend container is running"
else
    print_status 1 "Backend container is NOT running - starting..."
    docker-compose up -d fastapi-backend
    sleep 5
fi

# Step 2: Test initial API health
echo ""
echo "📋 Step 2: Testing initial API health..."
HEALTH=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health)
HTTP_CODE=$(echo "$HEALTH" | tail -n1)
BODY=$(echo "$HEALTH" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    print_status 0 "Backend API is responding (HTTP 200)"
    echo "   Response: $BODY"
else
    print_status 1 "Backend API error (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
fi

# Step 3: Test database connectivity
echo ""
echo "📋 Step 3: Testing database connectivity..."
DB_READY=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health/ready)
DB_HTTP_CODE=$(echo "$DB_READY" | tail -n1)
DB_BODY=$(echo "$DB_READY" | head -n-1)

if [ "$DB_HTTP_CODE" = "200" ]; then
    print_status 0 "Database is connected"
    echo "   Response: $DB_BODY"
else
    print_status 1 "Database connection error"
fi

# Step 4: Check row counts before generation
echo ""
echo "📋 Step 4: Checking database row counts (before)..."
BEFORE=$(docker exec postgres-db psql -U postgres -d costdb -c "
SELECT 
  (SELECT COUNT(*) FROM subscriptions) as subscriptions,
  (SELECT COUNT(*) FROM resource_groups) as resource_groups,
  (SELECT COUNT(*) FROM resources) as resources,
  (SELECT COUNT(*) FROM services) as services,
  (SELECT COUNT(*) FROM cost_usage) as cost_usage;
" 2>/dev/null | tail -1)

echo "   $BEFORE"

# Step 5: Generate data
echo ""
echo "📋 Step 5: Generating synthetic data..."
echo "   (This may take 1-2 minutes...)"
docker exec fastapi-backend python /app/scripts/generate_data.py
GEN_RESULT=$?

if [ $GEN_RESULT -eq 0 ]; then
    print_status 0 "Data generation completed"
else
    print_status 1 "Data generation failed (exit code: $GEN_RESULT)"
fi

# Step 6: Check row counts after generation
echo ""
echo "📋 Step 6: Checking database row counts (after)..."
AFTER=$(docker exec postgres-db psql -U postgres -d costdb -c "
SELECT 
  (SELECT COUNT(*) FROM subscriptions) as subscriptions,
  (SELECT COUNT(*) FROM resource_groups) as resource_groups,
  (SELECT COUNT(*) FROM resources) as resources,
  (SELECT COUNT(*) FROM services) as services,
  (SELECT COUNT(*) FROM cost_usage) as cost_usage;
" 2>/dev/null | tail -1)

echo "   $AFTER"

# Step 7: Restart backend
echo ""
echo "📋 Step 7: Restarting backend service..."
docker-compose restart fastapi-backend
sleep 5
print_status 0 "Backend restarted"

# Step 8: Test API health after restart
echo ""
echo "📋 Step 8: Testing API health after restart..."
HEALTH_AFTER=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health)
HTTP_CODE_AFTER=$(echo "$HEALTH_AFTER" | tail -n1)
BODY_AFTER=$(echo "$HEALTH_AFTER" | head -n-1)

if [ "$HTTP_CODE_AFTER" = "200" ]; then
    print_status 0 "Backend is healthy after restart"
else
    print_status 1 "Backend error after restart (HTTP $HTTP_CODE_AFTER)"
fi

# Step 9: Test cost summary endpoint
echo ""
echo "📋 Step 9: Testing /api/v1/cost/summary endpoint..."
COST=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/cost/summary)
COST_HTTP=$(echo "$COST" | tail -n1)
COST_BODY=$(echo "$COST" | head -n-1)

if [ "$COST_HTTP" = "200" ]; then
    print_status 0 "Cost summary endpoint working (HTTP 200)"
    echo "   Response: $(echo "$COST_BODY" | head -c 100)..."
else
    print_status 1 "Cost summary endpoint error (HTTP $COST_HTTP)"
    echo "   Error: $COST_BODY"
fi

# Step 10: Test resources endpoint
echo ""
echo "📋 Step 10: Testing /api/v1/resources/top-expensive endpoint..."
RESOURCES=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/resources/top-expensive)
RES_HTTP=$(echo "$RESOURCES" | tail -n1)
RES_BODY=$(echo "$RESOURCES" | head -n-1)

if [ "$RES_HTTP" = "200" ]; then
    print_status 0 "Resources endpoint working (HTTP 200)"
    echo "   Response: $(echo "$RES_BODY" | head -c 100)..."
else
    print_status 1 "Resources endpoint error (HTTP $RES_HTTP)"
    echo "   Error: $RES_BODY"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✨ Debug report complete!"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo "═══════════════════════════════════════════════════════════"
