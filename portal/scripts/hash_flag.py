#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 portal/scripts/hash_flag.py 'FLAG{example}'", file=sys.stderr)
        return 1

    flag = sys.argv[1].strip()
    print(hashlib.sha256(flag.encode("utf-8")).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
