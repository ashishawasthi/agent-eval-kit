"""A promotion-gate HTTP client: one contract for a service's ``--mode gate``.

At promotion, a model or agent's quality is checked against a shared promotion-gate service (an
"AI quality" / model-risk service). Two calls, both fail-closed:

* ``evaluate`` -> ``POST /v1/evaluations {target, dataset_id, bundle}`` -> :class:`EvalReport`,
  parsed from the response ``results`` list (NOT ``metrics``), each row carrying its
  server-owned threshold, passed through unchanged.
* ``gate``     -> ``POST /v1/gate {target, dataset_id, bundle}`` -> ``{"passed": bool}``.

Metric selection is by the registered bundle name (the service owns the metric set + per-bundle
thresholds); no bare metric names go on the wire, so the service's fail-closed unknown-metric
rejection can never be triggered by this client. ``dataset_id`` is sent at both the top level
and inside ``target`` because the service 422s if they diverge.

Kept dependency-light: the ``Authorization`` / signed-actor headers are injectable
(``auth_headers=``), so a consumer can pass ``hex_service_kit.s2s.client_headers()`` without this
package depending on it, and the base-URL https guard is inlined.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import PurePath
from urllib.parse import urlparse

import httpx

from .report import EvalMetricResult, EvalReport

_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=5.0)
#: Prompt/agent version tag; bump when the prompt corpus changes, or source it from a registry.
_DEFAULT_PROMPT_VERSION = "v1"

AuthHeaders = Mapping[str, str] | Callable[[], Mapping[str, str]]


class GateClientError(RuntimeError):
    """Raised when the gate service returns a non-2xx response or is unreachable."""


def _require_secure_url(url: str, *, service: str) -> str:
    """Return ``url`` trimmed; reject plaintext non-loopback URLs (https-only S2S transport)."""
    cleaned = (url or "").rstrip("/")
    parsed = urlparse(cleaned)
    if parsed.scheme == "https":
        return cleaned
    if parsed.scheme == "http" and (parsed.hostname or "") in _LOOPBACK_HOSTS:
        return cleaned
    raise ValueError(
        f"{service}: refusing gate base URL {url!r}: promotion-gate calls must use https:// "
        "(plain http is allowed only for localhost development)"
    )


class PromotionGateClient:
    """HTTP client for a promotion-gate ("AI quality" / model-risk) service."""

    def __init__(
        self,
        base_url: str,
        *,
        bundle: str,
        model: str,
        prompt_version: str = _DEFAULT_PROMPT_VERSION,
        auth_headers: AuthHeaders | None = None,
        timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = _require_secure_url(base_url, service=type(self).__name__)
        self._bundle = bundle
        self._model = model
        self._prompt_version = prompt_version
        self._auth_headers = auth_headers
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        source = self._auth_headers
        if source is None:
            return {}
        resolved = source() if callable(source) else source
        return dict(resolved)

    def _request_body(self, dataset_path: str) -> dict[str, object]:
        """Build the structured request body from a dataset path.

        ``dataset_id`` is the dataset file's basename without ``.jsonl`` and is sent at both the
        top level (the service loads the data from it) and inside ``target`` (the service requires
        them equal; a divergence is a 422).
        """
        dataset_id = PurePath(dataset_path).name.removesuffix(".jsonl")
        return {
            "target": {
                "model": self._model,
                "prompt_version": self._prompt_version,
                "dataset_id": dataset_id,
                "system": "",
            },
            "dataset_id": dataset_id,
            "bundle": self._bundle,
        }

    def evaluate(self, dataset_path: str) -> EvalReport:
        """Score ``dataset_path`` via the gate service and return an :class:`EvalReport`."""
        url = f"{self._base_url}/v1/evaluations"
        try:
            response = httpx.post(
                url,
                json=self._request_body(dataset_path),
                timeout=self._timeout,
                headers=self._headers(),
            )
        except httpx.HTTPError as exc:
            raise GateClientError(f"gate request to {url} failed: {exc}") from exc
        if response.status_code // 100 != 2:
            raise GateClientError(
                f"gate service {url} returned {response.status_code}: {response.text[:500]}"
            )
        return self._parse(dataset_path, response.json())

    def gate(self, target: str) -> bool:
        """Promotion gate: True iff the service reports ``target`` passes.

        POSTs ``/v1/gate`` (not GET) so a missing dataset is a hard error, never a silent
        ``{"passed": false}`` indistinguishable from a real FAIL.
        """
        url = f"{self._base_url}/v1/gate"
        try:
            response = httpx.post(
                url,
                json=self._request_body(target),
                timeout=self._timeout,
                headers=self._headers(),
            )
        except httpx.HTTPError as exc:
            raise GateClientError(f"gate request to {url} failed: {exc}") from exc
        if response.status_code // 100 != 2:
            raise GateClientError(
                f"gate service {url} returned {response.status_code}: {response.text[:500]}"
            )
        body = response.json()
        return bool(body.get("passed", False))

    @staticmethod
    def _parse(dataset_path: str, body: dict[str, object]) -> EvalReport:
        # The service returns per-metric rows under "results" (NOT "metrics"); each row carries the
        # server-owned per-bundle threshold, which we pass through unchanged.
        raw = body.get("results")
        rows = raw if isinstance(raw, list) else []
        results = tuple(
            EvalMetricResult(
                metric=str(item.get("metric", "")),
                score=float(item.get("score", 0.0) or 0.0),
                threshold=float(item.get("threshold", 0.0) or 0.0),
                passed=bool(item.get("passed", False)),
            )
            for item in rows
            if isinstance(item, dict)
        )
        return EvalReport(dataset=dataset_path, results=results, n_examples=0)
