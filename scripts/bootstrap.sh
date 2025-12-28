#!/bin/bash
# Bootstrap script - Verifies prerequisites for release PR workflow

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔍 Checking prerequisites..."

# Check git
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi
echo "✅ git found: $(git --version)"

# Check GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "   Install: https://cli.github.com/"
    exit 1
fi
echo "✅ gh found: $(gh --version | head -1)"

# Check gh auth status
if ! gh auth status &> /dev/null; then
    echo "❌ Error: GitHub CLI is not authenticated"
    echo "   Run: gh auth login"
    exit 1
fi
echo "✅ GitHub CLI authenticated"

# Check we're in a git repo
if ! git rev-parse --git-dir &> /dev/null; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi
echo "✅ In git repository"

# Check repo.config.json exists
if [ ! -f "${REPO_ROOT}/repo.config.json" ]; then
    echo "❌ Error: repo.config.json not found"
    exit 1
fi
echo "✅ repo.config.json found"

echo ""
echo "✅ All prerequisites met!"
echo ""
echo "Next steps:"
echo "  make verify  - Run quality gates"
echo "  make pr      - Create release PR"
echo "  make meta    - Update repo metadata (optional)"

