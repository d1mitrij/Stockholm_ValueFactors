"""
run_all_eps_factors.py — Parallel runner for all EPS Value Factor scripts.

Mirrors WifOR's ``run_all_value_factors.py``:
  - Discovers indicator scripts via glob on indicators/*.py
  - Runs each as a subprocess with ThreadPoolExecutor
  - Logs execution time and status per script
  - Writes a timestamped execution log

Usage
─────
  python run_all_eps_factors.py [--max-workers 4] [--timeout 600] [--verbose]
  python run_all_eps_factors.py --list
  python run_all_eps_factors.py --only inorganic_gases particles voc
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from config import list_indicators

logger = logging.getLogger(__name__)


def _discover_scripts(only: list[str] | None = None) -> list[tuple[str, Path]]:
    """Return (indicator_key, script_path) pairs, optionally filtered."""
    indicators_dir = ROOT / "indicators"
    all_scripts = sorted(indicators_dir.glob("[0-9][0-9][0-9]_prepare_*_eps.py"))

    results = []
    for script in all_scripts:
        # Extract indicator key from filename: 001_prepare_inorganic_gases_eps.py → inorganic_gases
        stem = script.stem  # e.g. "001_prepare_inorganic_gases_eps"
        parts = stem.split("_prepare_", 1)
        if len(parts) < 2:
            continue
        key = parts[1].removesuffix("_eps")

        if only and key not in only:
            continue
        results.append((key, script))

    return results


def _run_script(key: str, script: Path, timeout: int, verbose: bool) -> dict:
    """Run one indicator script as a subprocess; return status dict."""
    start = time.monotonic()
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=not verbose,
            timeout=timeout,
            text=True,
        )
        elapsed = time.monotonic() - start
        ok = result.returncode == 0
        return {
            "key":     key,
            "script":  script.name,
            "ok":      ok,
            "elapsed": elapsed,
            "stdout":  result.stdout or "",
            "stderr":  result.stderr or "",
            "error":   None if ok else f"returncode={result.returncode}",
        }
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return {
            "key": key, "script": script.name, "ok": False,
            "elapsed": elapsed, "stdout": "", "stderr": "",
            "error": f"Timed out after {timeout}s",
        }
    except Exception as exc:
        elapsed = time.monotonic() - start
        return {
            "key": key, "script": script.name, "ok": False,
            "elapsed": elapsed, "stdout": "", "stderr": "",
            "error": str(exc),
        }


def _write_log(results: list[dict], log_path: Path) -> None:
    lines = [
        f"EPS Value Factors — Execution Log",
        f"Generated: {datetime.now().isoformat()}",
        "=" * 60,
    ]
    for r in results:
        status = "OK" if r["ok"] else "FAILED"
        lines.append(f"[{status}] {r['key']:30s}  {r['elapsed']:6.1f}s  {r['script']}")
        if r["error"]:
            lines.append(f"       Error: {r['error']}")
        if r["stderr"]:
            for line in r["stderr"].splitlines()[:10]:
                lines.append(f"       STDERR: {line}")
    lines.append("=" * 60)
    total = sum(r["elapsed"] for r in results)
    n_ok = sum(r["ok"] for r in results)
    lines.append(f"Total: {n_ok}/{len(results)} scripts succeeded, wall-clock ≈ {total:.0f}s")
    log_path.write_text("\n".join(lines))
    logger.info("Execution log: %s", log_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all EPS Value Factor indicator scripts in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--max-workers", type=int, default=4,
                        help="Thread pool size (default: 4)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Per-script timeout in seconds (default: 600)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print subprocess stdout/stderr live")
    parser.add_argument("--list", action="store_true",
                        help="List indicators and exit")
    parser.add_argument("--only", nargs="+", metavar="KEY",
                        help="Run only these indicator keys")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.list:
        print("\nAvailable EPS indicator keys:")
        for key, script_id, desc in list_indicators():
            print(f"  {script_id}  {key:<28}  {desc}")
        return

    scripts = _discover_scripts(only=args.only)
    if not scripts:
        logger.error("No indicator scripts found (check indicators/ directory)")
        sys.exit(1)

    logger.info("Running %d indicator scripts with up to %d workers …",
                len(scripts), args.max_workers)

    results: list[dict] = []
    wall_start = time.monotonic()

    with ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {
            pool.submit(_run_script, key, script, args.timeout, args.verbose): key
            for key, script in scripts
        }
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            status = "✓" if r["ok"] else "✗"
            logger.info("%s  %-28s  %.1fs", status, r["key"], r["elapsed"])
            if not r["ok"]:
                logger.error("  FAILED: %s", r["error"])

    wall_elapsed = time.monotonic() - wall_start
    n_ok = sum(r["ok"] for r in results)
    logger.info(
        "\nCompleted: %d/%d succeeded  |  wall-clock %.1fs  (sequential would be ≈%.0fs)",
        n_ok, len(results), wall_elapsed, sum(r["elapsed"] for r in results),
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = ROOT / f"execution_log_{ts}.txt"
    _write_log(results, log_path)

    if n_ok < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
