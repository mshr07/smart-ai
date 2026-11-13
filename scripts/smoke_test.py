"""Python DevOps script 2: verify the running deployment over HTTP."""

import json
import os
from urllib.request import Request, urlopen

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def fetch(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        BASE_URL + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urlopen(request, timeout=10) as response:
        return response.status, json.load(response)


def main():
    status, health = fetch("/health")
    assert status == 200 and health["status"] == "ok", health

    status, ticket = fetch(
        "/tickets", {"text": "I was charged twice for my membership, urgent help"}
    )
    assert status == 201, ticket
    assert ticket["category"] in {"billing", "login", "technical"}, ticket
    assert ticket["priority"] == "high", ticket

    status, stored = fetch(f"/tickets/{ticket['ticket_id']}")
    assert status == 200 and stored["id"] == ticket["ticket_id"], stored
    print("SMOKE TEST PASSED: health, inference, and database persistence work")


if __name__ == "__main__":
    main()
