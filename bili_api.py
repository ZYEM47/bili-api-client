#!/usr/bin/env python3
"""Bilibili 搜索/评论 API 客户端（免登录，纯 Python 标准库）。

B 站接口对来源与请求头较敏感，以下设置可提升可用性：
1. 如所在网络访问受限，可走代理（从 https_proxy / HTTPS_PROXY 环境变量读取）
2. 使用常见的浏览器 UA（过于简单的 UA 容易被拒绝，返回 412）
3. 带上完整的常规请求头：Accept / Referer / Accept-Language
4. buvid3 cookie 经官方 finger/spi 接口获取，进程内缓存复用

已知限制：view 接口（视频详情）在部分网络环境下仍可能 412；search + reply 正常。
用法：
  bili_api.py search "Python 教程" [page] [page_size]
  bili_api.py replies <aid> [pn] [ps]
"""
import json, os, re, sys, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
PROXY = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
_BUVID3 = None

def _opener():
    if PROXY:
        return urllib.request.build_opener(
            urllib.request.ProxyHandler({"https": PROXY, "http": PROXY}))
    return urllib.request.build_opener()

def get_buvid3():
    global _BUVID3
    if _BUVID3:
        return _BUVID3
    req = urllib.request.Request(
        "https://api.bilibili.com/x/frontend/finger/spi",
        headers={"User-Agent": UA, "Referer": "https://www.bilibili.com/"})
    with _opener().open(req, timeout=15) as r:
        _BUVID3 = json.loads(r.read().decode())["data"]["b_3"]
    return _BUVID3

def _get(url, timeout=20, retries=3):
    last = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "application/json",
                "Referer": "https://www.bilibili.com/",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cookie": f"buvid3={get_buvid3()}",
            })
            with _opener().open(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001 - retry then raise
            last = e
    raise last

def clean(s):
    return re.sub(r"<[^>]+>", "", s or "")

def bili_search(keyword, page=1, page_size=50):
    url = ("https://api.bilibili.com/x/web-interface/search/type?search_type=video"
           f"&keyword={urllib.parse.quote(keyword)}&order=pubdate"
           f"&page={page}&page_size={page_size}")
    return _get(url)

def bili_replies(aid, pn=1, ps=20, sort=2):
    url = (f"https://api.bilibili.com/x/v2/reply?pn={pn}&ps={ps}"
           f"&type=1&oid={aid}&sort={sort}")
    return _get(url)

def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "search":
        d = bili_search(argv[2], int(argv[3]) if len(argv) > 3 else 1,
                        int(argv[4]) if len(argv) > 4 else 50)
        for v in d["data"]["result"]:
            print(f"{v['bvid']} | aid={v['aid']} | {clean(v['title'])[:60]} | {v['author'][:15]}")
    elif cmd == "replies":
        d = bili_replies(int(argv[2]), int(argv[3]) if len(argv) > 3 else 1,
                         int(argv[4]) if len(argv) > 4 else 20)
        data = d.get("data") or {}
        print(f"total={data.get('page', {}).get('count', '?')}")
        for r in data.get("replies", []) or []:
            print(f"[{r['member']['uname'][:14]} 赞{r['like']}] {clean(r['content']['message'])[:150]}")
    else:
        print(f"unknown cmd: {cmd}")
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
