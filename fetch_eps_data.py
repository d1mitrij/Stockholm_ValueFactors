#!/usr/bin/env python3
"""
fetch_eps_data.py — Download the EPS 2015d.1 source XLSX files.

Downloads one or both EPS 2015d.1 variants from the Swedish Life Cycle Center
(Chalmers University of Technology) and places them in the data/ directory
that config.py expects.

Source
------
  https://www.lifecyclecenter.se/publications/eps-2015d1-excluding-climate-impacts-from-secondary-particles/

Files
-----
  4a — EPS 2015d.1  including climate impacts from secondary particles (Report 2015:4a)
  4b — EPS 2015dx.1 excluding climate impacts from secondary particles (Report 2015:4b)

Usage
-----
  python fetch_eps_data.py              # download both variants (default)
  python fetch_eps_data.py --variant 4a # only the 4a (with secondary particles)
  python fetch_eps_data.py --variant 4b # only the 4b (without secondary particles)
  python fetch_eps_data.py --check      # check status of existing files without downloading
  python fetch_eps_data.py --force      # re-download even if files already exist

Notes
-----
  The downloaded files are © Swedish Life Cycle Center 2015.
  They are provided for local use only and must not be redistributed.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Allow running from the project root or from within eps_value_factors/
sys.path.insert(0, str(Path(__file__).parent))

from config import COMMON_PATHS, SOURCE_URLS

PUBLISHER = (
    "Swedish Life Cycle Center, Chalmers University of Technology, Gothenburg, Sweden"
)
LICENSE_NOTE = (
    "These files are © Swedish Life Cycle Center 2015. "
    "They are downloaded for local use only and must not be redistributed."
)


# ── Progress display ────────────────────────────────────────────────────────────

def _reporthook(downloaded: int, chunk: int, total: int) -> None:
    mb_done = downloaded / 1_048_576
    if total > 0:
        pct = min(100, downloaded * 100 // total)
        mb_total = total / 1_048_576
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(
            f"\r    [{bar}] {pct:3d}%  {mb_done:.1f}/{mb_total:.1f} MB",
            end="",
            flush=True,
        )
    else:
        print(f"\r    {mb_done:.1f} MB downloaded", end="", flush=True)


# ── Download / check helpers ────────────────────────────────────────────────────

def _file_status(dest: Path) -> str:
    if not dest.exists():
        return "MISSING"
    size_mb = dest.stat().st_size / 1_048_576
    return f"OK  ({size_mb:.1f} MB,  {dest})"


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept": "application/octet-stream,*/*",
}

_CHUNK = 65_536  # 64 KiB read chunks


def _download(url: str, dest: Path) -> bool:
    """
    Download *url* to *dest*, showing a progress bar.
    Sends a browser User-Agent (servers block Python's default agent).
    Returns True on success, False on error.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    print(f"    {url}")
    print(f"    → {dest}")
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with tmp.open("wb") as fh:
                while True:
                    chunk = resp.read(_CHUNK)
                    if not chunk:
                        break
                    fh.write(chunk)
                    downloaded += len(chunk)
                    _reporthook(downloaded, _CHUNK, total)
        print()  # newline after progress bar
        tmp.rename(dest)
        size_mb = dest.stat().st_size / 1_048_576
        print(f"    Saved: {size_mb:.1f} MB")
        return True
    except urllib.error.HTTPError as exc:
        print(f"\n    ERROR (HTTP {exc.code}): {exc.reason}")
    except urllib.error.URLError as exc:
        print(f"\n    ERROR (network): {exc.reason}")
    except OSError as exc:
        print(f"\n    ERROR (I/O): {exc}")
    except Exception as exc:  # noqa: BLE001
        print(f"\n    ERROR: {exc}")
    if tmp.exists():
        tmp.unlink()
    return False


# ── CLI ─────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Download EPS 2015d.1 source XLSX files from the Swedish Life Cycle Center.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--variant",
        choices=["both", "4a", "4b"],
        default="both",
        help="Which variant to download: 4a (with secondary particles), "
             "4b (without), or both (default: both)",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to save files (default: data/ as configured in config.py)",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Report file status without downloading",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if file already exists",
    )
    return p


def main() -> int:
    args = _build_parser().parse_args()

    variants = ["4a", "4b"] if args.variant == "both" else [args.variant]

    # Resolve output directory: CLI override or the directory from config.py
    if args.output_dir is not None:
        out_dir = args.output_dir
    else:
        # Use the directory that config.COMMON_PATHS["eps_xlsx_with_secondary"] lives in
        out_dir = Path(COMMON_PATHS["eps_xlsx_with_secondary"]).parent

    print()
    print("EPS 2015d.1 — Source Data Fetch")
    print(f"Publisher  : {PUBLISHER}")
    print(f"Output dir : {out_dir}")
    print(f"License    : {LICENSE_NOTE}")
    print()

    any_failure = False

    for key in variants:
        src = SOURCE_URLS[key]
        dest = out_dir / src["filename"]

        print(f"[{key}]  {src['description']}")
        print(f"       {src['report']}")

        if args.check:
            print(f"       Status: {_file_status(dest)}")
            if not dest.exists():
                any_failure = True
            print()
            continue

        if dest.exists() and not args.force:
            size_mb = dest.stat().st_size / 1_048_576
            print(f"       Already present ({size_mb:.1f} MB) — skipping.  Use --force to re-download.")
            print()
            continue

        ok = _download(src["url"], dest)
        if not ok:
            any_failure = True
        print()

    # ── Summary ──────────────────────────────────────────────────────────────
    if not args.check:
        print("─" * 60)
        for key in variants:
            dest = out_dir / SOURCE_URLS[key]["filename"]
            print(f"  {_file_status(dest)}")
        print()

        if not any_failure:
            print("Next step:")
            print("  python run_all_eps_factors.py --max-workers 4")
        else:
            print("One or more files could not be downloaded.")
            print("Check your network connection and retry.")
        print()

    return 1 if any_failure else 0


if __name__ == "__main__":
    sys.exit(main())
