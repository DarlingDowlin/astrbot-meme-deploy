#!/usr/bin/env python3
"""按文件并发下载表情包，支持完整性校验与原子替换。"""
import argparse, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor


def valid_gif(path: str) -> bool:
    try:
        if os.path.getsize(path) < 100:
            return False
        with open(path, 'rb') as f:
            f.seek(-1, os.SEEK_END)
            return f.read(1) == b'\x3b'
    except OSError:
        return False


def fetch(rel: str, base: str, dest: str, retries: int = 3) -> tuple[bool, str]:
    out = os.path.join(dest, rel)
    final_ok = lambda: os.path.isfile(out) and valid_gif(out)
    if final_ok():
        return True, rel
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + '.part'
    url = f"{base.rstrip('/')}/{rel}"
    for _ in range(retries):
        r = subprocess.run(
            ['curl', '-sfL', '--connect-timeout', '10', '-m', '180', '-o', tmp, url],
            capture_output=True,
        )
        if r.returncode == 0 and valid_gif(tmp):
            os.replace(tmp, out)
            return True, rel
        if os.path.exists(tmp):
            os.remove(tmp)
    return False, rel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', required=True, help='每行一个相对路径')
    ap.add_argument('--base', required=True, help='URL 前缀')
    ap.add_argument('--dest', required=True, help='本地目录')
    ap.add_argument('--workers', type=int, default=10)
    args = ap.parse_args()

    with open(args.list, encoding='utf-8') as f:
        paths = [l.strip() for l in f if l.strip()]

    os.makedirs(args.dest, exist_ok=True)
    ok = bad = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for success, rel in ex.map(lambda p: fetch(p, args.base, args.dest), paths):
            if success:
                ok += 1
            else:
                bad += 1
                print(f'FAIL {rel}', file=sys.stderr)

    print(f'done: {ok} ok, {bad} failed')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
