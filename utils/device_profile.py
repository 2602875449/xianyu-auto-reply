"""Utilities for emulating a realistic Xianyu web (PC) browser profile."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Mapping, Optional


@dataclass(frozen=True)
class _BrowserCandidate:
    """Represents a single desktop browser fingerprint option."""

    os_description: str
    chrome_version: str
    sec_ch_ua: str
    sec_ch_ua_platform: str

    def build_user_agent(self) -> str:
        """Compose a realistic User-Agent string for the desktop browser."""
        return (
            "Mozilla/5.0 ({os_description}) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
        ).format(os_description=self.os_description, chrome_version=self.chrome_version)

    def description(self) -> str:
        return f"{self.os_description} / Chrome {self.chrome_version}"


_BROWSER_POOL = (
    _BrowserCandidate(
        os_description="Windows NT 10.0; Win64; x64",
        chrome_version="120.0.6099.224",
        sec_ch_ua='"Chromium";v="120", "Not=A?Brand";v="24", "Google Chrome";v="120"',
        sec_ch_ua_platform='"Windows"',
    ),
    _BrowserCandidate(
        os_description="Windows NT 10.0; Win64; x64",
        chrome_version="121.0.6167.185",
        sec_ch_ua='"Google Chrome";v="121", "Not=A?Brand";v="24", "Chromium";v="121"',
        sec_ch_ua_platform='"Windows"',
    ),
    _BrowserCandidate(
        os_description="Windows NT 11.0; Win64; x64",
        chrome_version="122.0.6261.128",
        sec_ch_ua='"Chromium";v="122", "Not=A?Brand";v="24", "Google Chrome";v="122"',
        sec_ch_ua_platform='"Windows"',
    ),
    _BrowserCandidate(
        os_description="Windows NT 10.0; Win64; x64",
        chrome_version="140.0.7132.86",
        sec_ch_ua='"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        sec_ch_ua_platform='"Windows"',
    ),
)


def _canonical_header_key(key: str) -> str:
    """Normalise header casing to avoid duplicates."""
    lowered = key.strip().lower()
    if not lowered:
        return key

    return "-".join(part.capitalize() if part else part for part in key.strip().split("-"))


@dataclass
class RealDeviceProfile:
    """Encapsulates a concrete browser profile used for outgoing requests."""

    candidate: _BrowserCandidate
    accept_language: str = "zh,zh-CN;q=0.9,en;q=0.8"
    origin: str = "https://www.goofish.com"
    referer: str = "https://www.goofish.com/"

    def user_agent(self) -> str:
        return self.candidate.build_user_agent()

    def describe(self) -> str:
        return self.candidate.description()

    def build_http_headers(
        self,
        base_headers: Optional[Mapping[str, str]] = None,
        cookie: Optional[str] = None,
    ) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if base_headers:
            for key, value in base_headers.items():
                headers[_canonical_header_key(key)] = value

        headers.update(
            {
                "Accept": headers.get("Accept", "application/json"),
                "Accept-Language": headers.get("Accept-Language", self.accept_language),
                "Content-Type": headers.get("Content-Type", "application/x-www-form-urlencoded"),
                "Origin": headers.get("Origin", self.origin),
                "Referer": headers.get("Referer", self.referer),
                "Priority": headers.get("Priority", "u=1, i"),
                "Sec-Ch-Ua": headers.get("Sec-Ch-Ua", self.candidate.sec_ch_ua),
                "Sec-Ch-Ua-Mobile": headers.get("Sec-Ch-Ua-Mobile", "?0"),
                "Sec-Ch-Ua-Platform": headers.get(
                    "Sec-Ch-Ua-Platform", self.candidate.sec_ch_ua_platform
                ),
                "Sec-Fetch-Dest": headers.get("Sec-Fetch-Dest", "empty"),
                "Sec-Fetch-Mode": headers.get("Sec-Fetch-Mode", "cors"),
                "Sec-Fetch-Site": headers.get("Sec-Fetch-Site", "same-site"),
                "User-Agent": self.user_agent(),
            }
        )

        if cookie:
            headers["Cookie"] = cookie
        return headers

    def build_websocket_headers(
        self,
        base_headers: Optional[Mapping[str, str]] = None,
        cookie: Optional[str] = None,
    ) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if base_headers:
            for key, value in base_headers.items():
                headers[_canonical_header_key(key)] = value

        headers.update(
            {
                "Accept-Encoding": headers.get("Accept-Encoding", "gzip, deflate, br"),
                "Accept-Language": headers.get("Accept-Language", self.accept_language),
                "Cache-Control": headers.get("Cache-Control", "no-cache"),
                "Origin": headers.get("Origin", self.origin),
                "Pragma": headers.get("Pragma", "no-cache"),
                "User-Agent": self.user_agent(),
            }
        )

        if cookie:
            headers["Cookie"] = cookie
        return headers


def get_device_profile(identifier: Optional[str] = None) -> RealDeviceProfile:
    """Return a deterministic but varied browser profile for the provided identifier."""
    rng = random.Random()
    if identifier:
        rng.seed(identifier)
    candidate = rng.choice(_BROWSER_POOL)
    return RealDeviceProfile(candidate=candidate)


__all__ = ["RealDeviceProfile", "get_device_profile"]
