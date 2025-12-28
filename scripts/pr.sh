#!/bin/bash
# Release PR creation script
# Creates a branch, runs quality gates, commits, and opens a PR

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load config
CONFIG_FILE="${REPO_ROOT}/repo.config.json"
if [ ! -f "${CONFIG_FILE}" ]; then
    echo "❌ Error: repo.config.json not found"
    exit 1
fi

# Parse config (requires jq or python)
if command -v jq &> /dev/null; then
    REPO_NAME=$(jq -r '.repo_name' "${CONFIG_FILE}")
    REPO_TYPE=$(jq -r '.repo_type' "${CONFIG_FILE}")
    DEFAULT_BRANCH=$(jq -r '.default_branch' "${CONFIG_FILE}")
    REVIEWERS=$(jq -r '.reviewers | join(",")' "${CONFIG_FILE}")
    LABELS=$(jq -r '.labels | join(",")' "${CONFIG_FILE}")
    INSTALL_CMD=$(jq -r '.commands.install' "${CONFIG_FILE}")
    LINT_CMD=$(jq -r '.commands.lint' "${CONFIG_FILE}")
    FORMAT_CMD=$(jq -r '.commands.format_check' "${CONFIG_FILE}")
    TYPECHECK_CMD=$(jq -r '.commands.typecheck' "${CONFIG_FILE}")
    TEST_CMD=$(jq -r '.commands.test' "${CONFIG_FILE}")
    REQUIRED_FILES=$(jq -r '.required_files[]' "${CONFIG_FILE}")
else
    # Fallback to python if jq not available
    REPO_NAME=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['repo_name'])")
    REPO_TYPE=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['repo_type'])")
    DEFAULT_BRANCH=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['default_branch'])")
    REVIEWERS=$(python3 -c "import json; print(','.join(json.load(open('${CONFIG_FILE}'))['reviewers']))")
    LABELS=$(python3 -c "import json; print(','.join(json.load(open('${CONFIG_FILE}'))['labels']))")
    INSTALL_CMD=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['commands']['install'])")
    LINT_CMD=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['commands']['lint'])")
    FORMAT_CMD=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['commands']['format_check'])")
    TYPECHECK_CMD=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['commands']['typecheck'])")
    TEST_CMD=$(python3 -c "import json; print(json.load(open('${CONFIG_FILE}'))['commands']['test'])")
    REQUIRED_FILES=$(python3 -c "import json; [print(f) for f in json.load(open('${CONFIG_FILE}'))['required_files']]")
fi

# Generate branch name
BRANCH_DATE=$(date +%Y-%m-%d)
BRANCH_NAME="chore/release-pr-${BRANCH_DATE}"

echo "🚀 Creating release PR for ${REPO_NAME}"
echo "   Type: ${REPO_TYPE}"
echo "   Branch: ${BRANCH_NAME}"
echo ""

cd "${REPO_ROOT}"

# Check if branch already exists
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    echo "⚠️  Branch ${BRANCH_NAME} already exists"
    read -p "Delete and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -D "${BRANCH_NAME}" || true
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

# Ensure we're on default branch and up to date
CURRENT_BRANCH=$(git branch --show-current)
if [ "${CURRENT_BRANCH}" != "${DEFAULT_BRANCH}" ]; then
    echo "📥 Checking out ${DEFAULT_BRANCH}"
    git checkout "${DEFAULT_BRANCH}"
fi

echo "📥 Pulling latest changes..."
git pull origin "${DEFAULT_BRANCH}" || true

# Create new branch
echo "🌿 Creating branch: ${BRANCH_NAME}"
git checkout -b "${BRANCH_NAME}"

# Check required files exist
echo ""
echo "📋 Checking required files..."
MISSING_FILES=()
for file in ${REQUIRED_FILES}; do
    if [ ! -f "${REPO_ROOT}/${file}" ]; then
        MISSING_FILES+=("${file}")
        echo "  ❌ Missing: ${file}"
    else
        echo "  ✅ Found: ${file}"
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    echo "❌ Error: Missing required files:"
    printf "   - %s\n" "${MISSING_FILES[@]}"
    echo "   Please create these files before running make pr"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
eval "${INSTALL_CMD}" || {
    echo "❌ Error: Installation failed"
    echo "   Command: ${INSTALL_CMD}"
    exit 1
}

# Run quality gates
echo ""
echo "🔍 Running quality gates..."

# Lint
echo "  Running lint..."
if ! eval "${LINT_CMD}" > /tmp/lint_output.txt 2>&1; then
    echo "❌ Lint failed"
    cat /tmp/lint_output.txt
    echo ""
    echo "Fix lint errors and run: make verify"
    exit 1
fi
echo "  ✅ Lint passed"

# Format check
echo "  Running format check..."
if ! eval "${FORMAT_CMD}" > /tmp/format_output.txt 2>&1; then
    echo "❌ Format check failed"
    cat /tmp/format_output.txt
    echo ""
    echo "Fix formatting and run: make format"
    exit 1
fi
echo "  ✅ Format check passed"

# Typecheck
echo "  Running typecheck..."
if ! eval "${TYPECHECK_CMD}" > /tmp/typecheck_output.txt 2>&1; then
    echo "❌ Typecheck failed"
    cat /tmp/typecheck_output.txt
    echo ""
    echo "Fix type errors and run: make verify"
    exit 1
fi
echo "  ✅ Typecheck passed"

# Tests
echo "  Running tests..."
if ! eval "${TEST_CMD}" > /tmp/test_output.txt 2>&1; then
    echo "❌ Tests failed"
    cat /tmp/test_output.txt
    echo ""
    echo "Fix test failures and run: make verify"
    exit 1
fi
echo "  ✅ Tests passed"

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    echo ""
    echo "⚠️  No changes to commit"
    echo "   Branch: ${BRANCH_NAME}"
    echo "   You can push manually or delete the branch"
    exit 0
fi

# Commit changes
echo ""
echo "💾 Committing changes..."
git add -A
git commit -m "chore: release readiness updates

- Updated documentation and metadata
- Verified quality gates (lint, format, typecheck, tests)
- All required files present"

# Push branch
echo ""
echo "📤 Pushing branch..."
git push -u origin "${BRANCH_NAME}" || {
    echo "❌ Error: Failed to push branch"
    exit 1
}

# Generate PR body
PR_BODY_FILE=$(mktemp)
cat > "${PR_BODY_FILE}" <<EOF
## Release Readiness: ${REPO_NAME}

**Date:** ${BRANCH_DATE}
**Type:** ${REPO_TYPE}

### Summary

This PR includes release readiness updates:
- ✅ Documentation and metadata verified
- ✅ Quality gates passed
- ✅ Required files present

### Quality Gates Passed

- [x] Lint: \`${LINT_CMD}\`
- [x] Format: \`${FORMAT_CMD}\`
- [x] Typecheck: \`${TYPECHECK_CMD}\`
- [x] Tests: \`${TEST_CMD}\`

### Required Files

$(for file in ${REQUIRED_FILES}; do echo "- [x] \`${file}\`"; done)

### How to Test

\`\`\`bash
# Run quality gates
make verify

# Run tests
make test

# (Optional) Run live smoke tests
ETHYS_MODE=live make test-live
\`\`\`

### Notes

- All changes are automated via \`make pr\`
- Quality gates must pass before merging
- Review checklist in PR template
EOF

PR_BODY=$(cat "${PR_BODY_FILE}")

# Create PR
echo ""
echo "🔨 Creating PR..."
PR_ARGS=(
    "pr" "create"
    "--title" "Release readiness: ${REPO_NAME} (${BRANCH_DATE})"
    "--body" "${PR_BODY}"
    "--base" "${DEFAULT_BRANCH}"
    "--head" "${BRANCH_NAME}"
)

if [ -n "${LABELS}" ] && [ "${LABELS}" != "null" ]; then
    PR_ARGS+=("--label" "${LABELS}")
fi

if [ -n "${REVIEWERS}" ] && [ "${REVIEWERS}" != "null" ] && [ "${REVIEWERS}" != "" ]; then
    PR_ARGS+=("--reviewer" "${REVIEWERS}")
fi

PR_URL=$(gh "${PR_ARGS[@]}")

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PR created successfully!"
    echo "   ${PR_URL}"
    echo ""
    echo "Next steps:"
    echo "  1. Review the PR"
    echo "  2. Ensure CI passes"
    echo "  3. Merge when ready"
else
    echo "❌ Error: Failed to create PR"
    exit 1
fi

