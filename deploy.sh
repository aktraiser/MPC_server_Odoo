#!/bin/bash

# Deploy script for Odoo MCP Server on Render
set -e

echo "🚀 Preparing Odoo MCP Server for Render deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

print_status "Docker is available"

# Check if all required files exist
required_files=("Dockerfile" "requirements-docker.txt" "render.yaml" "odoo_mcp_server/server.py")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

print_status "All required files present"

# Build Docker image locally for testing
echo "🔨 Building Docker image..."
if docker build -t odoo-mcp-server-test .; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Test the Docker image
echo "🧪 Testing Docker image..."
if docker run --rm -e ODOO_URL=https://demo.odoo.com -e ODOO_DATABASE=demo -e ODOO_USERNAME=admin -e ODOO_PASSWORD=admin odoo-mcp-server-test python -c "import odoo_mcp_server; print('✅ Import successful')"; then
    print_status "Docker image test passed"
else
    print_error "Docker image test failed"
    exit 1
fi

# Clean up test image
docker rmi odoo-mcp-server-test

echo ""
echo "🎉 Deployment preparation completed successfully!"
echo ""
echo "📋 Next steps for Render deployment:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add Docker configuration for Render'"
echo "   git push origin main"
echo ""
echo "2. In Render dashboard:"
echo "   - Create new Web Service"
echo "   - Connect your GitHub repository"
echo "   - Render will auto-detect Dockerfile"
echo "   - Set environment variables:"
echo "     * ODOO_URL: Your Odoo instance URL"
echo "     * ODOO_DATABASE: Your database name"
echo "     * ODOO_USERNAME: Your username"
echo "     * ODOO_PASSWORD: Your password"
echo ""
echo "3. Deploy and test!"
echo ""
print_status "Ready for Render deployment! 🚀"