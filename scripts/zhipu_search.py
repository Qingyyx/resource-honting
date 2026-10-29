#!/usr/bin/env python3
"""按需调用智谱搜狗搜索，输出 JSON；凭据从环境或技能目录 .env 读取。"""

import argparse
import json
import os
from pathlib import Path
import re
import socket
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/web_search"
ENGINE = "search_pro_sogou"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class SearchError(Exception):
    def __init__(self, kind, status=None, code=None):
        self.details = {"kind": kind}
        if status is not None:
            self.details["http_status"] = status
        if code is not None:
            self.details["code"] = code


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # 凭据只发送给固定的官方端点。
        return None


def load_api_key():
    for name in ("ZHIPU_API_KEY", "ZHIPUAI_API_KEY"):
        if os.environ.get(name, "").strip():
            return os.environ[name].strip()
    try:
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SearchError("missing_credentials") from None
    except OSError:
        raise SearchError("credentials_unreadable") from None
    for name in ("ZHIPU_API_KEY", "ZHIPUAI_API_KEY"):
        for line in lines:
            field, sep, value = line.strip().partition("=")
            if sep and field == name:
                value = value.strip().strip("\"'")
                if value:
                    return value
    raise SearchError("missing_credentials")


def safe_code(data):
    error = data.get("error") if isinstance(data, dict) else None
    code = error.get("code") if isinstance(error, dict) else None
    # 不输出服务端原始错误文本，避免回显认证信息。
    if code is not None and re.fullmatch(r"[0-9]{1,8}", str(code)):
        return str(code)
    return None


def search(query, count=10, domain=None, freshness="noLimit", content_size="medium", timeout=30):
    key = load_api_key()
    payload = {
        "search_query": query,
        "search_engine": ENGINE,
        "search_intent": False,
        "count": count,
        "content_size": content_size,
    }
    if domain:
        payload["search_domain_filter"] = domain
    # 官方说明同时指定域名和时间过滤时 count 不生效。
    if freshness != "noLimit":
        payload["search_recency_filter"] = freshness
    request = Request(
        ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            data = json.load(response)
    except HTTPError as exc:
        try:
            code = safe_code(json.load(exc))
        except (ValueError, OSError):
            code = None
        kind = {401: "authentication", 403: "permission", 402: "quota", 429: "rate_limit"}.get(exc.code, "http_error")
        raise SearchError(kind, status=exc.code, code=code) from None
    except (TimeoutError, socket.timeout):
        raise SearchError("timeout") from None
    except URLError as exc:
        kind = "timeout" if isinstance(exc.reason, (TimeoutError, socket.timeout)) else "network"
        raise SearchError(kind) from None
    except OSError:
        raise SearchError("network") from None
    except ValueError:
        raise SearchError("invalid_json") from None
    if not isinstance(data, dict):
        raise SearchError("invalid_response")
    if "error" in data:
        raise SearchError("api_error", code=safe_code(data))
    results = data.get("search_result")
    if not isinstance(results, list) or any(not isinstance(item, dict) for item in results):
        raise SearchError("invalid_response")
    return {
        "provider": "zhipu",
        "engine": ENGINE,
        "query": query,
        "status": "ok" if results else "empty",
        "result_count": len(results),
        "request_id": data.get("request_id"),
        "created": data.get("created"),
        "search_result": results,
    }


def query_value(value):
    value = value.strip()
    if not value or len(value) > 70:
        raise argparse.ArgumentTypeError("查询词需为 1–70 个字符")
    return value


def domain_value(value):
    if not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?", value):
        raise argparse.ArgumentTypeError("域名仅填写主机名，例如 zhihu.com 或 qq.com")
    return value


def timeout_value(value):
    try:
        value = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("超时需为数字") from None
    if not 0 < value <= 120:
        raise argparse.ArgumentTypeError("超时需大于 0 且不超过 120 秒")
    return value


def main():
    parser = argparse.ArgumentParser(description="智谱搜狗搜索：腾讯新闻/企鹅号、知乎等内容按需使用")
    parser.add_argument("query", type=query_value)
    parser.add_argument("--count", type=int, choices=(10, 20, 30, 40, 50), default=10)
    parser.add_argument("--domain", type=domain_value, help="可选单个域名；默认不限制，保留相关来源")
    parser.add_argument("--freshness", choices=("noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"), default="noLimit")
    parser.add_argument("--content-size", choices=("medium", "high"), default="medium")
    parser.add_argument("--timeout", type=timeout_value, default=30)
    args = parser.parse_args()
    try:
        result = search(args.query, args.count, args.domain, args.freshness, args.content_size, args.timeout)
    except SearchError as exc:
        print(json.dumps({"provider": "zhipu", "engine": ENGINE, "status": "error", "error": exc.details}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
