#!/bin/bash

# Simple Docker Deployment Script for AFS Assessment Framework

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

## Detect docker compose command (new CLI vs legacy)
if docker compose version >/dev/null 2>&1; then
    DC="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DC="docker-compose"
else
    log_error "Neither 'docker compose' nor 'docker-compose' is available. Please install Docker Compose."
    exit 1
fi

case "$1" in
    build)
        log_info "Building Docker image..."
        $DC build
        ;;
    up|start)
        log_info "Starting application..."
        $DC up -d
        log_info "Application started at http://localhost:5001"
        ;;
    down|stop)
        log_info "Stopping application and removing volumes..."
        $DC down -v
        ;;
    logs)
        $DC logs -f
        ;;
    shell)
        log_info "Accessing application shell..."
        $DC exec app bash
        ;;
    setup)
        log_info "Setting up database..."
        $DC exec app python scripts/setup_database.py
        ;;
    *)
        echo "Usage: $0 {build|start|stop|logs|shell|setup}"
        echo "  build - Build the Docker image"
        echo "  start - Start the application"
        echo "  stop  - Stop the application"
        echo "  logs  - View application logs"
        echo "  shell - Access application shell"
        echo "  setup - Run database setup script"
        exit 1
        ;;
esac
