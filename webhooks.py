"""Webhook verification utilities for CrewAI integrations."""

from typing import Any

from echorift.webhooks import verify_blockwire, verify_cronsynth, verify_switchboard


def verify_webhook(request: Any, service: str, secret: str) -> bool:
    """
    Verify a webhook signature from an EchoRift service.
    
    Works with Flask, FastAPI, and other frameworks that provide
    request.data and request.headers.
    
    Args:
        request: The HTTP request object
        service: Service name ("blockwire", "cronsynth", or "switchboard")
        secret: Webhook secret
    
    Returns:
        True if the signature is valid
    
    Example (Flask):
        @app.post("/webhook/blockwire")
        def handle_blockwire():
            if not verify_webhook(request, "blockwire", WEBHOOK_SECRET):
                return "Invalid", 401
            # Process event...
    
    Example (FastAPI):
        @app.post("/webhook/blockwire")
        async def handle_blockwire(request: Request):
            body = await request.body()
            if not verify_webhook_raw(body, dict(request.headers), "blockwire", SECRET):
                raise HTTPException(401)
            # Process event...
    """
    # Get body as bytes
    if hasattr(request, "data"):
        body = request.data  # Flask
    elif hasattr(request, "body"):
        body = request.body  # Some frameworks
    else:
        raise ValueError("Cannot extract body from request object")
    
    # Ensure bytes
    if isinstance(body, str):
        body = body.encode()
    
    # Get headers as dict
    headers = dict(request.headers)
    
    return verify_webhook_raw(body, headers, service, secret)


def verify_webhook_raw(
    body: bytes,
    headers: dict,
    service: str,
    secret: str,
) -> bool:
    """
    Verify a webhook signature with raw body and headers.
    
    Args:
        body: Raw request body as bytes
        headers: Request headers as dict
        service: Service name ("blockwire", "cronsynth", or "switchboard")
        secret: Webhook secret
    
    Returns:
        True if the signature is valid
    """
    service = service.lower()
    
    if service == "blockwire":
        return verify_blockwire(body, headers, secret)
    elif service == "cronsynth":
        return verify_cronsynth(body, headers, secret)
    elif service == "switchboard":
        return verify_switchboard(body, headers, secret)
    else:
        raise ValueError(f"Unknown service: {service}")
