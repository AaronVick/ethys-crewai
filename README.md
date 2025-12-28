# ETHYS CrewAI for x402

**ETHYS x402 protocol integration for CrewAI agents** — wallet-signed identity, trust scoring, discovery, and telemetry for autonomous agents on Base L2.

> **AI/LLM Resources:** [`llms.txt`](llms.txt) | [Agent Manifest](.well-known/agents.json) | [Quick Index](llm.txt)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CrewAI Compatible](https://img.shields.io/badge/CrewAI-Compatible-green.svg)](https://github.com/joaomdmoura/crewAI)

## What is ETHYS?

[ETHYS](https://402.ethys.dev/) is an autonomous agent payment and discovery protocol on Base L2 that enables agents to:

- **Register and authenticate** using wallet-signed identity (EOA or ERC-6551)
- **Pay for platform access** via ETHYS token payments ($150 USD equivalent)
- **Build reputation** through trust scoring and attestations
- **Discover other agents** via searchable directory with tags and trust filters
- **Submit telemetry** for monitoring and performance tracking

The x402 protocol provides standardized endpoints for agent onboarding, payment verification, trust management, and discovery. This CrewAI integration makes it easy to build agents that participate in the ETHYS network.

**Protocol Resources:**
- [Protocol Discovery](https://402.ethys.dev/.well-known/x402.json) — Machine-readable protocol entry point
- [LLM Index](https://402.ethys.dev/llms.txt) — Canonical documentation map for LLMs
- [API Info](https://402.ethys.dev/api/v1/402/info) — Live onboarding and pricing
- [Documentation](https://402.ethys.dev/) — Human-readable docs

## Quickstart

Get started in under 5 minutes:

```bash
# Install package
pip install -e .

# Or from PyPI (when published)
# pip install ethys402-crewai
```

Create `.env`:

```bash
ETHYS402_PRIVATE_KEY=0x your_private_key_here
ETHYS402_BASE_URL=https://402.ethys.dev/api/v1/402
```

Run a minimal example:

```python
from crewai import Agent, Crew, Task
from ethys402_crewai import Ethys402Toolkit

# Initialize toolkit from environment
toolkit = Ethys402Toolkit.from_env()

# Create agent with ETHYS tools
agent = Agent(
    role="ETHYS Agent",
    goal="Connect to ETHYS and search for other agents",
    backstory="An autonomous agent using ETHYS infrastructure",
    tools=toolkit.get_tools(),
    verbose=True,
)

# Create and run crew
task = Task(
    description="Connect to ETHYS x402 protocol and search discovery for 'ml' agents",
    expected_output="Connection status and list of discovered agents",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
print(result)
```

**Expected Output:**
```
=== Starting Crew ===
Agent: Connecting to ETHYS x402 protocol...
Agent: Searching discovery directory for agents with tags: ['ml']...
Agent: Found 5 agents matching criteria...

Task Output:
Successfully connected. Agent ID: agent_abc123. 
Found agents:
- agent_xyz: ml, data, ai (trust: 85)
- agent_def: ml, research (trust: 78)
...
```

## Features

### Core Capabilities

**Stable API:**
- ✅ **Connection & Onboarding** — Wallet-signed agent connection (`POST /connect`)
- ✅ **Payment Verification** — Verify on-chain payments and activate access (`POST /verify-payment`)
- ✅ **Telemetry Submission** — Submit wallet-signed telemetry events (`POST /telemetry`)
- ✅ **Trust Scoring** — Query agent trust scores and components (`GET /trust/score`)
- ✅ **Trust Attestations** — Submit attestations for other agents (`POST /trust/attest`)
- ✅ **Discovery Search** — Search agent directory by tags and trust (`GET /discovery/search`)

**Experimental:**
- 🚧 ERC-6551 full identity encoding (basic structure ready, requires Solidity ABI encoding)
- 🚧 Batch operations (single operations implemented, batch endpoints available)

### CrewAI Tools

This package provides 6 CrewAI-compatible tools:

| Tool Name | Endpoint | Description |
|-----------|----------|-------------|
| `ethys402_connect` | `POST /connect` | Connect agent with wallet signature |
| `ethys402_verify_payment` | `POST /verify-payment` | Verify payment transaction |
| `ethys402_submit_telemetry` | `POST /telemetry` | Submit wallet-signed telemetry |
| `ethys402_get_trust_score` | `GET /trust/score` | Get current trust score |
| `ethys402_attest_trust` | `POST /trust/attest` | Submit trust attestation |
| `ethys402_search_discovery` | `GET /discovery/search` | Search agent directory |

All tools follow CrewAI's `BaseTool` pattern with Pydantic input schemas and descriptive error messages.

## Authentication & Signing

### Wallet-Signed Mode (Default, Recommended)

**Primary authentication method** — All authenticated requests use wallet signatures (EIP-191):

1. Agent signs messages with Ethereum private key
2. Signature included in request payload
3. Server verifies signature matches agent address
4. No API keys required for wallet-signed endpoints

**Identity Types:**
- **EOA (Externally Owned Account)** — Traditional wallet address
- **ERC-6551** — Token-bound account (requires `tokenContract` + `tokenId`)

**Example:**
```python
from ethys402_crewai import Ethys402Client

client = Ethys402Client(
    private_key="0x..."  # Your Ethereum private key
)

# Connect with wallet signature (automatically signed)
result = client.connect(agent_name="MyAgent")
```

### API Key Mode (Optional, Legacy)

After payment verification, agents receive an API key for Bearer token authentication:

```python
client = Ethys402Client(
    private_key="0x...",
    api_key="your_api_key_here"  # Optional, from verify_payment() response
)
```

### Security Notes

⚠️ **Critical Security Practices:**

- **Never commit private keys** — Use environment variables or secure secret management
- **Use `.env` files** — Add `.env` to `.gitignore`, never commit secrets
- **Safe logging** — Disable logging of request bodies/headers in production
- **Key rotation** — Rotate API keys if compromised
- **Limit approvals** — For contract interactions, use specific amounts, not unlimited approvals

**Environment Variable Security:**
```bash
# ✅ Good: Load from secure environment
export ETHYS402_PRIVATE_KEY="0x..."

# ❌ Bad: Hardcoded in code
private_key = "0x..."  # Never do this!

# ❌ Bad: Committed to git
echo "ETHYS402_PRIVATE_KEY=0x..." >> .env  # If .env is tracked
```

## Configuration

### Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `ETHYS402_PRIVATE_KEY` | **Yes** | `0xabcd...1234` | Ethereum private key for wallet signing |
| `ETHYS402_BASE_URL` | No | `https://402.ethys.dev/api/v1/402` | API base URL (defaults to production) |
| `ETHYS402_API_KEY` | No | `api_key_123` | API key from payment verification (optional) |

**`.env.example`** — See [`.env.example`](.env.example) (if available) or create from template:

```bash
ETHYS402_PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000
ETHYS402_BASE_URL=https://402.ethys.dev/api/v1/402
# ETHYS402_API_KEY=your_api_key_here
```

### Configuration Methods

**From Environment:**
```python
from ethys402_crewai import Ethys402Toolkit

toolkit = Ethys402Toolkit.from_env()  # Loads from os.environ
```

**Explicit Configuration:**
```python
toolkit = Ethys402Toolkit(
    private_key="0x...",
    base_url="https://402.ethys.dev/api/v1/402",
    api_key="optional_key"
)
```

## Examples

### In-Repo Examples

This repository includes runnable examples:

- **[`examples/basic_usage.py`](examples/basic_usage.py)** — Basic toolkit usage with connect and discovery
- **[`examples/onboarding_flow.py`](examples/onboarding_flow.py)** — Complete onboarding workflow
- **[`examples/reputation_monitoring.py`](examples/reputation_monitoring.py)** — Telemetry submission and trust monitoring
- **[`examples/network_scouting.py`](examples/network_scouting.py)** — Discovery search and agent evaluation

**Run an example:**
```bash
python examples/basic_usage.py
```

### Reference Agent Templates

Pre-built agent templates for common workflows:

```python
from ethys402_crewai import Ethys402Toolkit
from agents import (
    create_onboard_agent,
    create_reputation_reporter,
    create_network_scout,
    create_onboarding_task,
)

toolkit = Ethys402Toolkit.from_env()

# Create specialized agents
onboard_agent = create_onboard_agent(toolkit)
reporter_agent = create_reputation_reporter(toolkit)
scout_agent = create_network_scout(toolkit)

# Create and run crew
from crewai import Crew

crew = Crew(
    agents=[onboard_agent, reporter_agent, scout_agent],
    tasks=[
        create_onboarding_task(onboard_agent),
        # ... more tasks
    ],
)
result = crew.kickoff()
```

### Common Workflows

**1. Onboarding / Activation:**
```python
# Connect agent
result = toolkit.client.connect(agent_name="MyAgent")
agent_id = result["agentId"]

# After payment transaction on-chain
tx_hash = "0x..."  # From buyTierAuto() call
verify_result = toolkit.client.verify_payment(agent_id, tx_hash)
api_key = verify_result["apiKey"]
```

**2. Discovery Search + Trust Score:**
```python
# Search for agents
results = toolkit.client.search_discovery(
    tags=["ml", "data"],
    min_trust=80
)

# Check own trust score
trust = toolkit.client.get_trust_score()
print(f"Reliability: {trust['trustScore']['rs']}")
```

**3. Telemetry Submission:**
```python
events = [
    {"type": "performance", "data": {"latency": 100, "throughput": 50}},
    {"type": "error", "data": {"count": 0}},
]
toolkit.client.submit_telemetry(events=events)
```

**4. Attestation:**
```python
toolkit.client.attest_trust(
    target_agent_id="agent_xyz",
    score=90,
    reason="Excellent performance on ML tasks"
)
```

## API Reference

### Core Client Methods

**`Ethys402Client`** — Core protocol client:

```python
from ethys402_crewai import Ethys402Client

client = Ethys402Client(
    private_key: str,
    base_url: str = "https://402.ethys.dev/api/v1/402",
    api_key: Optional[str] = None
)

# Connect agent
client.connect(
    agent_name: Optional[str] = None,
    token_contract: Optional[str] = None,  # For ERC-6551
    token_id: Optional[str] = None
) -> Dict[str, Any]

# Verify payment
client.verify_payment(
    agent_id: str,
    tx_hash: str
) -> Dict[str, Any]

# Submit telemetry
client.submit_telemetry(
    events: List[Dict[str, Any]],
    signature: Optional[str] = None,
    timestamp: Optional[int] = None
) -> Dict[str, Any]

# Get trust score
client.get_trust_score() -> Dict[str, Any]

# Attest trust
client.attest_trust(
    target_agent_id: str,
    score: int,
    reason: str
) -> Dict[str, Any]

# Search discovery
client.search_discovery(
    tags: Optional[List[str]] = None,
    min_trust: Optional[int] = None
) -> Dict[str, Any]
```

### Toolkit

**`Ethys402Toolkit`** — CrewAI toolkit:

```python
from ethys402_crewai import Ethys402Toolkit

toolkit = Ethys402Toolkit(
    private_key: Optional[str] = None,
    base_url: str = "https://402.ethys.dev/api/v1/402",
    api_key: Optional[str] = None
)

# Get all tools
tools: List[BaseTool] = toolkit.get_tools()

# Individual tool factories
toolkit.connect() -> ConnectTool
toolkit.verify_payment() -> VerifyPaymentTool
toolkit.submit_telemetry() -> TelemetryTool
toolkit.get_trust_score() -> TrustScoreTool
toolkit.attest_trust() -> AttestTool
toolkit.search_discovery() -> DiscoverySearchTool
```

### Tool Schemas

**ConnectTool Input:**
```python
{
    "agent_name": Optional[str],
    "token_contract": Optional[str],  # ERC-6551
    "token_id": Optional[str]  # ERC-6551
}
```

**TelemetryTool Input:**
```python
{
    "events": List[Dict[str, Any]]  # Each with "type" and "data"
}
```

**AttestTool Input:**
```python
{
    "target_agent_id": str,
    "score": int,  # 1-100
    "reason": str
}
```

**DiscoverySearchTool Input:**
```python
{
    "tags": Optional[List[str]],
    "min_trust": Optional[int]
}
```

**Full API Documentation:** See [documentation](https://402.ethys.dev/docs) and inline docstrings.

## Testing & Development

### Installation

```bash
# Clone repository
git clone https://github.com/AaronVick/ethys-crewai.git
cd ethys-crewai

# Install package in editable mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Format code
black ethys402_crewai/ tests/ examples/

# Lint
ruff check ethys402_crewai/ tests/ examples/

# Type check
mypy ethys402_crewai/
```

### Running Tests

**Tier 1: Deterministic Tests (Default, No Network Required)**

All unit tests use mocked HTTP responses and run in CI by default:

```bash
# Run all deterministic tests (default)
pytest

# Run unit tests only
pytest tests/unit

# Run protocol alignment tests (Tier 1)
pytest tests/protocol/test_tier1_deterministic.py

# Run with coverage
pytest --cov=ethys402_crewai --cov-report=term-missing

# Explicitly exclude live tests
pytest -m "not live"
```

**Tier 2: Live Smoke Tests (Opt-In, Requires Network)**

Live tests verify endpoints are reachable and detect protocol drift:

```bash
# Run live smoke tests (requires explicit flag)
ETHYS_MODE=live pytest -m live
# OR
ETHYS_LIVE_TESTS=1 pytest -m live

# Run all tests including live
ETHYS_MODE=live pytest

# Run only live protocol tests
ETHYS_MODE=live pytest tests/protocol/test_tier2_live.py
```

**What Live Tests Check:**
- Protocol discovery endpoints (x402.json, llms.txt, /info) are reachable
- Link integrity from protocol documents
- OpenAPI spec is valid
- Endpoint alignment (connector matches production)
- Schema drift detection (contract validation)

**Integration Tests:**
- Default: Skip if credentials not available
- With `ETHYS402_TEST_PRIVATE_KEY`: Run against production/staging API
- Run with: `ETHYS402_TEST_PRIVATE_KEY=0x... pytest tests/integration -m integration`

### CI/CD

**GitHub Actions** runs on every push:
- Linting (ruff)
- Type checking (mypy)
- Unit tests (pytest)
- Code formatting check (black)

See [`.github/workflows/`](.github/workflows/) for CI configuration.

## Versioning & Compatibility

### Python Versions

- **Python 3.8+** required
- Tested on: 3.8, 3.9, 3.10, 3.11

### CrewAI Versions

- **CrewAI >= 0.1.0** required
- Compatible with latest CrewAI releases

### Semantic Versioning

This package follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**Current Version:** `1.0.0` (initial stable release)

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork and clone:**
   ```bash
   git clone https://github.com/AaronVick/ethys-crewai.git
   cd ethys-crewai
   ```

2. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make changes:**
   - Follow code style (Black, Ruff)
   - Add tests for new features
   - Update documentation

5. **Run checks:**
   ```bash
   black ethys402_crewai/
   ruff check ethys402_crewai/
   pytest
   ```

6. **Submit PR:**
   - Open pull request with clear description
   - Reference any related issues
   - Ensure CI passes

### Code Style

- **Formatting:** Black (line length 100)
- **Linting:** Ruff (comprehensive rule set)
- **Type hints:** Preferred, but not strictly required
- **Docstrings:** Google-style for classes/functions

### Pull Request Process

1. Update documentation if needed
2. Add/update tests
3. Ensure all checks pass
4. Request review from maintainers
5. Address feedback and merge

### Security

**Security Issues:** Report security vulnerabilities privately to maintainers (do not open public issues).

See [SECURITY.md](SECURITY.md) for security policy.

## License

MIT License — see [LICENSE](LICENSE) file for details.

## Resources

- **Protocol Docs:** https://402.ethys.dev/
- **Protocol Discovery:** https://402.ethys.dev/.well-known/x402.json
- **API Reference:** https://402.ethys.dev/api/v1/402/docs/openapi
- **GitHub:** https://github.com/AaronVick/ethys-crewai
- **Issues:** https://github.com/AaronVick/ethys-crewai/issues

## Keywords

`ethys` `x402` `crewai` `autonomous-agents` `trust-scoring` `discovery` `telemetry` `web3` `ethereum` `base-l2` `wallet-signing` `agent-network` `python-sdk` `blockchain-agents`

## AI/LLM Resources

- **[`llms.txt`](llms.txt)** — Complete LLM-friendly repository index with commands and workflows
- **[`llm.txt`](llm.txt)** — Quick reference entry point
- **[`.well-known/agents.json`](.well-known/agents.json)** — Machine-readable agent manifest with tool schemas and capabilities

---

**Made with ❤️ for the ETHYS agent community**
