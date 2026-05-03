#!/bin/bash

# QUICK START - Generate data and reload backend in one command
# This is the easiest way to generate data without "Failed to fetch" errors

# Make sure we're in the project root
if [ ! -f docker-compose.yml ]; then
    echo "❌ Error: docker-compose.yml not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Azure Cost Simulator - Generate Data (One Click)     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Generate and reload in one command
echo "Starting data generation and backend reload..."
echo ""

docker exec fastapi-backend python /app/scripts/generate_data.py && \
docker-compose restart fastapi-backend && \
sleep 5 && \
echo "" && \
echo "✅ Success! Data generated and backend restarted." && \
echo "" && \
echo "🌐 Frontend: http://localhost:5173" && \
echo "📚 API Docs: http://localhost:8000/docs" && \
echo "" && \
echo "👉 Refresh your browser now to see the generated data."

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error occurred. Run the detailed script for debugging:"
    echo "   bash scripts/debug_and_generate.sh"
fi
