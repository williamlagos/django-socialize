"""
HTTP Signatures implementation compliant with draft-cavage-http-signatures
for ActivityPub federation with Mastodon, Pixelfed, PeerTube, and other Fediverse nodes.
"""

import base64
import email.utils
import hashlib
import re
import time
from urllib.parse import urlparse

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from django.conf import settings


def generate_key_pair() -> tuple[str, str]:
    """Generates a 2048-bit RSA key pair in PEM format."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )

    return private_pem, public_pem


def build_digest(body: bytes) -> str:
    """Computes SHA-256 Digest header value for an HTTP payload."""
    sha256_hash = hashlib.sha256(body).digest()
    b64_hash = base64.b64encode(sha256_hash).decode("utf-8")
    return f"SHA-256={b64_hash}"


def build_signed_headers(
    private_key_pem: str,
    key_id: str,
    method: str,
    target_url: str,
    body: bytes = b"",
    headers: dict | None = None,
) -> dict[str, str]:
    """
    Constructs and signs HTTP headers for an outbound ActivityPub request.
    """
    parsed = urlparse(target_url)
    host = parsed.netloc
    path = parsed.path
    if parsed.query:
        path = f"{path}?{parsed.query}"
    if not path:
        path = "/"

    method = method.lower()
    req_headers = dict(headers or {})

    # Default ActivityPub content and accept types
    req_headers.setdefault("Host", host)
    req_headers.setdefault("Date", email.utils.formatdate(usegmt=True))
    req_headers.setdefault(
        "User-Agent",
        f'Socialize-ActivityPub ({getattr(settings, "SITE_DOMAIN", "localhost")})',
    )
    req_headers.setdefault(
        "Accept",
        'application/activity+json, application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
    )

    signed_header_names = ["(request-target)", "host", "date"]

    if body or method in ("post", "put", "patch"):
        req_headers["Digest"] = build_digest(body)
        req_headers.setdefault("Content-Type", "application/activity+json")
        signed_header_names.append("digest")
        signed_header_names.append("content-type")

    # Build signature payload
    lines = []
    for h in signed_header_names:
        if h == "(request-target)":
            lines.append(f"(request-target): {method} {path}")
        else:
            val = (
                req_headers.get(h)
                or req_headers.get(h.capitalize())
                or req_headers.get(h.title())
            )
            if val is None:
                # Case-insensitive lookup
                for k, v in req_headers.items():
                    if k.lower() == h.lower():
                        val = v
                        break
            lines.append(f"{h.lower()}: {val}")

    sign_string = "\n".join(lines).encode("utf-8")

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"),
        password=None,
    )
    raw_signature = private_key.sign(
        sign_string,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    b64_signature = base64.b64encode(raw_signature).decode("utf-8")

    headers_str = " ".join(signed_header_names)
    signature_header = (
        f'keyId="{key_id}",'
        f'algorithm="rsa-sha256",'
        f'headers="{headers_str}",'
        f'signature="{b64_signature}"'
    )

    req_headers["Signature"] = signature_header
    return req_headers


def parse_signature_header(header_val: str) -> dict[str, str]:
    """Parses draft-cavage Signature header key-value parameters."""
    params = {}
    pattern = re.compile(r'([a-zA-Z0-9_-]+)="([^"]*)"')
    for match in pattern.finditer(header_val):
        params[match.group(1)] = match.group(2)
    return params


def fetch_remote_public_key(key_id: str) -> str | None:
    """Fetches remote actor or public key document and returns PEM string."""
    try:
        resp = requests.get(
            key_id,
            headers={
                "Accept": 'application/activity+json, application/ld+json; profile="https://www.w3.org/ns/activitystreams"',
                "User-Agent": f'Socialize-ActivityPub ({getattr(settings, "SITE_DOMAIN", "localhost")})',
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if "publicKey" in data and isinstance(data["publicKey"], dict):
            return data["publicKey"].get("publicKeyPem")
        if "publicKeyPem" in data:
            return data.get("publicKeyPem")
        return None
    except Exception:
        return None


def verify_http_signature(request, fetch_actor_fn=None) -> tuple[bool, str | None]:
    """
    Verifies an incoming ActivityPub request's HTTP signature.
    Returns (True, keyId) on success, or (False, error_reason) on failure.
    """
    sig_header = request.headers.get("Signature") or request.META.get("HTTP_SIGNATURE")
    if not sig_header:
        return False, "Missing Signature header"

    params = parse_signature_header(sig_header)
    key_id = params.get("keyId")
    signature_b64 = params.get("signature")
    signed_headers_str = params.get("headers", "date")

    if not key_id or not signature_b64:
        return False, "Malformed Signature header"

    # Verify Date header clock skew (within 300s)
    date_val = request.headers.get("Date") or request.META.get("HTTP_DATE")
    if date_val:
        try:
            req_time = email.utils.parsedate_to_datetime(date_val).timestamp()
            current_time = time.time()
            if abs(current_time - req_time) > 300:
                return (
                    False,
                    "Signature Date header has expired or excessive clock drift",
                )
        except Exception:
            return False, "Invalid Date header format"

    # Verify Digest if present in body or signed headers
    signed_header_names = [h.strip().lower() for h in signed_headers_str.split()]
    if "digest" in signed_header_names:
        digest_val = request.headers.get("Digest") or request.META.get("HTTP_DIGEST")
        if not digest_val:
            return False, "Digest header required by signature but missing"
        expected_digest = build_digest(request.body)
        if digest_val != expected_digest:
            return (
                False,
                f"Digest header mismatch: got {digest_val}, expected {expected_digest}",
            )

    # Recreate signing string
    lines = []
    for h in signed_header_names:
        if h == "(request-target)":
            method = request.method.lower()
            path = request.get_full_path()
            lines.append(f"(request-target): {method} {path}")
        elif h == "host":
            host = request.get_host()
            lines.append(f"host: {host}")
        else:
            val = request.headers.get(h)
            if val is None:
                # Check META
                meta_key = f'HTTP_{h.upper().replace("-", "_")}'
                if meta_key in request.META:
                    val = request.META[meta_key]
                elif h == "content-type":
                    val = request.META.get("CONTENT_TYPE")
            if val is None:
                return False, f"Signed header {h} missing from request"
            lines.append(f"{h}: {val}")

    sign_string = "\n".join(lines).encode("utf-8")

    # Retrieve public key
    public_pem = None
    if fetch_actor_fn:
        public_pem = fetch_actor_fn(key_id)
    if not public_pem:
        public_pem = fetch_remote_public_key(key_id)

    if not public_pem:
        return False, f"Could not resolve public key for keyId {key_id}"

    try:
        public_key = serialization.load_pem_public_key(public_pem.encode("utf-8"))
        raw_sig = base64.b64decode(signature_b64)
        public_key.verify(
            raw_sig,
            sign_string,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True, key_id
    except InvalidSignature:
        return False, "Signature cryptographic verification failed"
    except Exception as e:
        return False, f"Error during signature verification: {str(e)}"
