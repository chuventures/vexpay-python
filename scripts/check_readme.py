"""Runs every ```python block in README.md against a live VEXPay API (use a local sandbox).

    VEXPAY_API_KEY=<test-mode key> VEXPAY_BASE_URL=http://127.0.0.1:3010 \
    VEXPAY_SANDBOX_OTP=<current sandbox token> python scripts/check_readme.py

The SDK's default base URL is pointed at VEXPAY_BASE_URL, ``input()`` answers
with VEXPAY_SANDBOX_OTP, and the webhook secret is a dummy — so each example
runs exactly as printed. Exits 1 on the first failing block.
"""

from __future__ import annotations

import builtins
import os
import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    base_url = os.environ.get("VEXPAY_BASE_URL")
    if not base_url or not os.environ.get("VEXPAY_API_KEY"):
        print("Set VEXPAY_API_KEY and VEXPAY_BASE_URL (a local/sandbox API).", file=sys.stderr)
        return 2

    import vexpay._core as core

    core.DEFAULT_BASE_URL = base_url.rstrip("/")
    os.environ.setdefault("VEXPAY_WEBHOOK_SECRET", "whsec_readme_check")
    otp = os.environ.get("VEXPAY_SANDBOX_OTP", "000000")
    builtins.input = lambda _prompt="": otp  # type: ignore[assignment]

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", readme, flags=re.DOTALL)
    for index, code in enumerate(blocks, start=1):
        # Configuration example hard-codes a localhost URL and a placeholder key.
        code = code.replace('"http://localhost:3010"', repr(base_url)).replace(
            '"sk_test_…"', repr(os.environ["VEXPAY_API_KEY"])
        )
        print(f"── example {index}/{len(blocks)} " + "─" * 40)
        try:
            exec(compile(code, f"README example {index}", "exec"), {"__name__": f"readme_example_{index}"})
        except Exception:  # noqa: BLE001 — report any failure with its traceback
            traceback.print_exc()
            print(f"README example {index} failed.", file=sys.stderr)
            return 1
    print(f"README: {len(blocks)} Python examples ran against {base_url}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
