"""Tests for ``get_base_url()`` host allowlist.

Background: Google rebranded NotebookLM to "Gemini Notebook" and began
redirecting notebooklm.google.com to notebook.google.com (issue #269).
``NOTEBOOKLM_BASE_URL=https://notebook.google.com`` must be accepted so users
can route API calls at the new domain, while non-Google hosts and non-https
schemes are still rejected.
"""

import pytest

from notebooklm_tools.utils.config import (
    _ALLOWED_BASE_HOSTS,
    NOTEBOOKLM_HOSTS,
    get_base_url,
)


def test_default_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NOTEBOOKLM_BASE_URL", raising=False)
    assert get_base_url() == "https://notebooklm.google.com"


@pytest.mark.parametrize(
    "value, expected",
    [
        # Gemini Notebook rebrand (issue #269).
        ("https://notebook.google.com", "https://notebook.google.com"),
        # Legacy personal host.
        ("https://notebooklm.google.com", "https://notebooklm.google.com"),
        # Enterprise host.
        ("https://notebooklm.cloud.google.com", "https://notebooklm.cloud.google.com"),
        # Trailing slashes are stripped.
        ("https://notebook.google.com/", "https://notebook.google.com"),
    ],
)
def test_allowed_base_urls(monkeypatch: pytest.MonkeyPatch, value: str, expected: str) -> None:
    monkeypatch.setenv("NOTEBOOKLM_BASE_URL", value)
    assert get_base_url() == expected


@pytest.mark.parametrize(
    "value",
    [
        # Non-https scheme is rejected.
        "http://notebook.google.com",
        # Unknown / spoofed hosts are rejected.
        "https://notebook.google.com.evil.example.com",
        "https://evil.example.com",
        "https://google.com",
    ],
)
def test_rejected_base_urls(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("NOTEBOOKLM_BASE_URL", value)
    with pytest.raises(ValueError):
        get_base_url()


def test_notebook_google_com_in_host_set() -> None:
    assert "notebook.google.com" in NOTEBOOKLM_HOSTS
    # Backwards-compatible alias still points at the canonical set.
    assert _ALLOWED_BASE_HOSTS is NOTEBOOKLM_HOSTS
