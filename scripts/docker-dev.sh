#!/bin/bash
# Development helper script for Docker

set -e

echo "🐳 Advanced Trade Insight Engine - Docker Development Helper"
echo "============================================================"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to build and start development environment
start_dev() {
    echo "🚀 Starting development environment..."
    docker-compose --profile dev up --build -d
    echo "✅ Development dashboard available at: http://localhost:8502"
}

# Function to run tests
run_tests() {
    echo "🧪 Running test suite..."
    docker-compose --profile test up --build test-runner
}

# Function to run pipeline
run_pipeline() {
    echo "⚙️ Running data processing pipeline..."
    docker-compose --profile pipeline up --build pipeline-runner
}

# Function to show logs
show_logs() {
    echo "📋 Showing application logs..."
    docker-compose logs -f insight-engine-dev
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up Docker resources..."
    docker-compose down -v
    docker system prune -f
    echo "✅ Cleanup complete"
}

# Function to show status
show_status() {
    echo "📊 Docker Services Status:"
    docker-compose ps
    echo ""
    echo "🌐 Available URLs:"
    echo "  • Production Dashboard: http://localhost:8501"
    echo "  • Development Dashboard: http://localhost:8502"
}

# Main menu
case "${1:-menu}" in
    "dev"|"start")
        check_docker
        start_dev
        ;;
    "test")
        check_docker
        run_tests
        ;;
    "pipeline")
        check_docker
        run_pipeline
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "clean")
        cleanup
        ;;
    "menu"|*)
        echo ""
        echo "Available commands:"
        echo "  ./scripts/docker-dev.sh dev      - Start development environment"
        echo "  ./scripts/docker-dev.sh test     - Run test suite"
        echo "  ./scripts/docker-dev.sh pipeline - Run data processing pipeline"
        echo "  ./scripts/docker-dev.sh logs     - Show application logs"
        echo "  ./scripts/docker-dev.sh status   - Show service status"
        echo "  ./scripts/docker-dev.sh clean    - Clean up Docker resources"
        echo ""
        echo "Quick start: ./scripts/docker-dev.sh dev"
        ;;
esac