#!/bin/bash

# Script to generate data and properly reload backend

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Azure Cost Simulator - Data Generation & Backend Reload  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if backend is running
echo "📋 Step 1: Checking backend status..."
if ! docker ps | grep -q fastapi-backend; then
    echo "⚠️  Backend not running. Starting..."
    docker-compose up -d fastapi-backend
    sleep 5
fi
echo "✅ Backend is running"

# Step 2: Generate synthetic data
echo ""
echo "📊 Step 2: Generating synthetic cost data..."
echo "   (This will take 1-2 minutes...)"
docker exec fastapi-backend python /app/scripts/generate_data.py

if [ $? -ne 0 ]; then
    echo "❌ Data generation failed!"
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "   - Check backend logs: docker logs fastapi-backend"
    echo "   - Check database: docker logs postgres-db"
    echo "   - Restart containers: docker-compose restart"
    exit 1
fi

echo "✅ Data generated successfully!"

# Step 3: Restart backend to refresh connection pools
echo ""
echo "🔄 Step 3: Restarting backend service..."
docker-compose restart fastapi-backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to start (this takes 10-15 seconds)..."
sleep 3

# Step 4: Wait for backend health check (with retries)
echo "🧪 Step 4: Verifying backend health..."
RETRY_COUNT=0
MAX_RETRIES=10

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy (HTTP 200)"
        break
    fi
    
    echo "⏳ Backend still initializing... (attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
    ((RETRY_COUNT++))
    sleep 2
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ Backend failed to become healthy after $MAX_RETRIES retries"
    echo ""
    echo "🔧 Manual troubleshooting:"
    echo "   - Check backend logs: docker logs fastapi-backend"
    echo "   - Check database logs: docker logs postgres-db"
    echo "   - Full restart: docker-compose down && docker-compose up -d"
    exit 1
fi

echo ""

# Step 5: Test API endpoints
echo "📋 Step 5: Testing key API endpoints..."

if curl -sf http://localhost:8000/api/v1/cost/summary > /dev/null 2>&1; then
    echo "✅ Cost endpoint working"
else
    echo "⚠️  Cost endpoint not responding"
fi

if curl -sf http://localhost:8000/api/v1/resources/top-expensive > /dev/null 2>&1; then
    echo "✅ Resources endpoint working"
else
    echo "⚠️  Resources endpoint not responding"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    ✨ All set! Ready to go                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Frontend:    http://localhost:5173"
echo "📚 API Docs:    http://localhost:8000/docs"
echo "📊 API Health:  http://localhost:8000/api/v1/health"
echo ""
echo "⚡ Next steps:"
echo "   1. Open your browser to http://localhost:5173"
echo "   2. Refresh the page to see the generated data"
echo "   3. Check the Dashboard, Cost Trends, and Resources pages"
echo ""

