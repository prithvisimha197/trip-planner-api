#!/bin/bash
# Build script with version tagging

# Get version from argument or use git commit hash
VERSION=${1:-$(git rev-parse --short HEAD 2>/dev/null || echo "latest")}

echo "🏗️  Building images with version: $VERSION"
echo ""

# Build with version
export VERSION
docker compose build

echo ""
echo "✅ Images built successfully!"
echo ""
echo "📦 Created tags:"
docker images | grep trip-planner | grep -E "$VERSION|latest"

echo ""
echo "💡 To run this version:"
echo "   VERSION=$VERSION docker compose up"
