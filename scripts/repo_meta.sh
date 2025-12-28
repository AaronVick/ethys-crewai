#!/bin/bash
# Repository metadata update script
# Updates repo description and topics via GitHub CLI

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load config
CONFIG_FILE="${REPO_ROOT}/repo.config.json"
if [ ! -f "${CONFIG_FILE}" ]; then
    echo "❌ Error: repo.config.json not found"
    exit 1
fi

# Parse config
if command -v jq &> /dev/null; then
    REPO_NAME=$(jq -r '.repo_name' "${CONFIG_FILE}")
    REPO_TYPE=$(jq -r '.repo_type' "${CONFIG_FILE}")
else
    REPO_NAME=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['repo_name'])")
    REPO_TYPE=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['repo_type'])")
fi

echo "📝 Updating repository metadata for ${REPO_NAME}"

# Get current repo info
REPO_FULL=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
if [ -z "${REPO_FULL}" ]; then
    echo "❌ Error: Could not determine repository"
    echo "   Make sure you're in a git repository with GitHub remote"
    exit 1
fi

echo "   Repository: ${REPO_FULL}"

# Determine description based on repo type
case "${REPO_TYPE}" in
    "crewai")
        DESCRIPTION="ETHYS x402 protocol integration for CrewAI agents — wallet-signed identity, trust scoring, discovery, and telemetry"
        ;;
    "langchain")
        DESCRIPTION="ETHYS x402 protocol integration for LangChain — wallet-signed identity, trust scoring, discovery, and telemetry"
        ;;
    "python")
        DESCRIPTION="ETHYS x402 Python SDK — wallet-signed identity, trust scoring, discovery, and telemetry for autonomous agents"
        ;;
    "examples")
        DESCRIPTION="ETHYS x402 protocol examples and reference implementations"
        ;;
    *)
        DESCRIPTION="ETHYS x402 protocol integration"
        ;;
esac

# Set description
echo "   Setting description..."
gh repo edit "${REPO_FULL}" --description "${DESCRIPTION}" || {
    echo "⚠️  Warning: Failed to set description (may not have permissions)"
}

# Set topics
echo "   Setting topics..."
TOPICS=(
    "ethys"
    "x402"
    "agents"
    "trust"
    "telemetry"
    "discovery"
    "web3"
    "ethereum"
    "base-l2"
    "wallet-signing"
    "agent-network"
)

# Add repo-type specific topics
case "${REPO_TYPE}" in
    "crewai")
        TOPICS+=("crewai" "python-sdk")
        ;;
    "langchain")
        TOPICS+=("langchain" "python-sdk")
        ;;
    "python")
        TOPICS+=("python-sdk")
        ;;
    "examples")
        TOPICS+=("examples" "reference")
        ;;
esac

# Join topics with comma
TOPICS_STR=$(IFS=,; echo "${TOPICS[*]}")

gh repo edit "${REPO_FULL}" --add-topic "${TOPICS_STR}" || {
    echo "⚠️  Warning: Failed to set topics (may not have permissions)"
}

echo ""
echo "✅ Repository metadata updated"
echo "   Description: ${DESCRIPTION}"
echo "   Topics: ${TOPICS_STR}"

