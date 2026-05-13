#!/bin/bash

# Kakeibo AI Local Development Utility Script

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.dev.yml"

function usage() {
    echo "Usage: $0 {setup|up|down|logs|test}"
    echo ""
    echo "Commands:"
    echo "  setup   Initialize local configuration and pull LLM models"
    echo "  up      Start the local development environment (Docker)"
    echo "  down    Stop the local development environment"
    echo "  logs    Show logs from the development environment"
    echo "  test    Run backend tests within the dev container"
    exit 1
}

function setup() {
    echo "🚀 Initializing local configuration..."

    # Create dev_local/config if not exists
    mkdir -p "$PROJECT_ROOT/dev_local/config"

    # Copy .env if not exists
    if [ ! -f "$PROJECT_ROOT/dev_local/.env" ]; then
        echo "Creating dev_local/.env from example..."
        cp "$PROJECT_ROOT/prod_local/.env.example" "$PROJECT_ROOT/dev_local/.env"
        # Append LLM defaults if not present
        if ! grep -q "LLM_PROVIDER" "$PROJECT_ROOT/dev_local/.env"; then
            echo "" >> "$PROJECT_ROOT/dev_local/.env"
            echo "# LLM Configuration" >> "$PROJECT_ROOT/dev_local/.env"
            echo "LLM_PROVIDER=ollama" >> "$PROJECT_ROOT/dev_local/.env"
            echo "OLLAMA_BASE_URL=http://ollama:11434" >> "$PROJECT_ROOT/dev_local/.env"
        fi
    fi

    # Copy config files from examples
    for example in "$PROJECT_ROOT/prod_local/config"/*.json.example; do
        config_name=$(basename "$example" .example)
        target="$PROJECT_ROOT/dev_local/config/$config_name"
        if [ ! -f "$target" ]; then
            echo "Creating $config_name from example..."
            cp "$example" "$target"
        fi
    done

    echo "✅ Configuration files initialized."
    echo ""
    read -p "Do you want to pull the Ollama model (llama3.2)? This may take some time. [y/N] " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        echo "Pulling llama3.2..."
        docker exec -it kakeibo-ollama ollama pull llama3.2 || {
            echo "Failed to pull via docker exec. Is the environment running?"
            echo "Attempting to pull using a temporary container..."
            docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull llama3.2
        }
        echo "✅ Model pull complete."
    else
        echo "Skipped model pull. You can do it later with: docker exec -it kakeibo-ollama ollama pull llama3.2"
    fi
}

function up() {
    echo "Starting development environment..."
    docker compose -f "$DOCKER_COMPOSE_FILE" up -d
    echo "✅ Environment started. Access dashboard at http://localhost:5173"
}

function down() {
    echo "Stopping development environment..."
    docker compose -f "$DOCKER_COMPOSE_FILE" down
    echo "✅ Environment stopped."
}

function logs() {
    docker compose -f "$DOCKER_COMPOSE_FILE" logs -f
}

function test() {
    echo "Running backend tests..."
    docker exec -it kakeibo-api-dev venv/bin/python3 -m pytest tests/ --ignore=tests/test_dashboard_e2e.py
}

case "$1" in
    setup) setup ;;
    up) up ;;
    down) down ;;
    logs) logs ;;
    test) test ;;
    *) usage ;;
esac
