#!/usr/bin/env python3
"""诊断 meme_manager 是否真的加载了表情包。"""
import argparse, json, sys
import urllib.request


def post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def get(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='http://127.0.0.1:6185')
    ap.add_argument('--user', default='astrbot')
    ap.add_argument('--password', required=True)
    args = ap.parse_args()

    try:
        login = post(f'{args.host}/api/auth/login',
                     {'username': args.user, 'password': args.password})
        token = login['data']['token']
    except Exception as e:
        print(f'login failed: {e}', file=sys.stderr)
        return 1

    try:
        packs = get(f'{args.host}/api/plug/meme_manager/packs', token)
    except Exception as e:
        print(f'query failed: {e}', file=sys.stderr)
        return 1

    for p in packs.get('packs', []):
        print(f"{p['id']:32} images={p['image_count']:4} cats={p['category_count']:2} "
              f"default={p['is_default']} enabled={p['enabled']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
