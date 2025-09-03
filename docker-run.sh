#!/bin/bash

# Apollo Docker Runner Script
# This script helps you run the Apollo pipeline using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Function to check if credentials directory exists
check_credentials() {
    if [ ! -d "credentials" ]; then
        print_warning "Credentials directory not found. Creating it..."
        mkdir -p credentials
        print_status "Please place your Google Cloud service account key file in the 'credentials' directory"
        print_status "Rename it to 'service-account-key.json'"
        return 1
    fi
    
    if [ ! -f "credentials/service-account-key.json" ]; then
        print_error "Service account key file not found at 'credentials/service-account-key.json'"
        print_status "Please place your Google Cloud service account key file in the 'credentials' directory"
        print_status "Rename it to 'service-account-key.json'"
        return 1
    fi
    
    print_success "Credentials file found"
    return 0
}

# Function to check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_status "Created .env file from template. Please edit it with your configuration."
        else
            print_error "env.example template not found"
            return 1
        fi
    fi
    
    print_success ".env file found"
    return 0
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully"
}

# Function to run the pipeline
run_pipeline() {
    print_status "Running Apollo labeling pipeline..."
    docker-compose run --rm apollo
    print_success "Pipeline completed successfully"
}

# Function to run in development mode
run_dev() {
    print_status "Running in development mode..."
    docker-compose run --rm apollo-dev
}

# Function to run validation
run_validation() {
    print_status "Running setup validation..."
    docker-compose run --rm apollo python validate_setup.py
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs apollo
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Apollo Docker Runner Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run the labeling pipeline"
    echo "  dev       Run in development mode (with live code mounting)"
    echo "  validate  Run setup validation"
    echo "  logs      Show container logs"
    echo "  cleanup   Clean up Docker resources"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build     # Build the image"
    echo "  $0 run       # Run the pipeline"
    echo "  $0 dev       # Run in development mode"
}

# Main script logic
main() {
    case "${1:-help}" in
        "build")
            check_docker
            build_image
            ;;
        "run")
            check_docker
            check_credentials || exit 1
            check_env || exit 1
            build_image
            run_pipeline
            ;;
        "dev")
            check_docker
            check_credentials || exit 1
            check_env || exit 1
            run_dev
            ;;
        "validate")
            check_docker
            check_credentials || exit 1
            check_env || exit 1
            build_image
            run_validation
            ;;
        "logs")
            check_docker
            show_logs
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
