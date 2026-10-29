"""验证官方参数约束、凭据读取和故障行为；不发送网络请求。"""

from contextlib import redirect_stderr, redirect_stdout
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import zhipu_search as client


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.credentials = patch.object(client, "load_api_key", return_value="test-only-credential")
        self.credentials.start()
        self.addCleanup(self.credentials.stop)

    def test_sogou_payload_and_results(self):
        response = {"request_id": "test-request", "search_result": [{"title": "测试", "link": "https://www.zhihu.com/question/1"}]}
        with patch.object(client, "build_opener") as opener:
            opener.return_value.open.return_value = BytesIO(json.dumps(response).encode())
            result = client.search("测试", domain="zhihu.com")
        request = opener.return_value.open.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "https://open.bigmodel.cn/api/paas/v4/web_search")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-only-credential")
        self.assertEqual(payload["search_engine"], "search_pro_sogou")
        self.assertFalse(payload["search_intent"])
        self.assertEqual(payload["count"], 10)
        self.assertEqual(payload["search_domain_filter"], "zhihu.com")
        self.assertNotIn("search_recency_filter", payload)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["search_result"], response["search_result"])

    def test_freshness_and_empty_results(self):
        with patch.object(client, "build_opener") as opener:
            opener.return_value.open.return_value = BytesIO(b'{"search_result": []}')
            result = client.search("测试", count=20, freshness="oneWeek")
        payload = json.loads(opener.return_value.open.call_args.args[0].data)
        self.assertEqual(payload["search_recency_filter"], "oneWeek")
        self.assertNotIn("search_domain_filter", payload)
        self.assertEqual(result["status"], "empty")

    def test_http_failures_do_not_retry_or_echo_credentials(self):
        for status, kind in ((401, "authentication"), (403, "permission"), (402, "quota"), (429, "rate_limit"), (500, "http_error")):
            with self.subTest(status=status), patch.object(client, "build_opener") as opener:
                body = json.dumps({"error": {"code": "1234", "message": "test-only-credential"}}).encode()
                opener.return_value.open.side_effect = HTTPError(client.ENDPOINT, status, "error", {}, BytesIO(body))
                with self.assertRaises(client.SearchError) as caught:
                    client.search("测试")
                self.assertEqual(caught.exception.details["kind"], kind)
                self.assertEqual(caught.exception.details["code"], "1234")
                self.assertNotIn("test-only-credential", json.dumps(caught.exception.details))
                opener.return_value.open.assert_called_once()

    def test_bad_responses_and_business_errors(self):
        for body, kind in ((b'not-json', "invalid_json"), (b'[]', "invalid_response"), (b'{}', "invalid_response"), (b'{"search_result": [null]}', "invalid_response"), (b'{"error": {"code": "1234"}}', "api_error")):
            with self.subTest(body=body), patch.object(client, "build_opener") as opener:
                opener.return_value.open.return_value = BytesIO(body)
                with self.assertRaises(client.SearchError) as caught:
                    client.search("测试")
                self.assertEqual(caught.exception.details["kind"], kind)

    def test_cli_network_failure_is_safe_and_nonzero(self):
        stdout, stderr = StringIO(), StringIO()
        with patch.object(client, "build_opener") as opener, patch.object(sys, "argv", ["zhipu_search.py", "测试"]), redirect_stdout(stdout), redirect_stderr(stderr):
            opener.return_value.open.side_effect = URLError("network test-only-credential")
            code = client.main()
        self.assertEqual(code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(json.loads(stderr.getvalue())["error"]["kind"], "network")
        self.assertNotIn("test-only-credential", stderr.getvalue())
        opener.return_value.open.assert_called_once()

    def test_cli_rejects_unsupported_sogou_count(self):
        with patch.object(sys, "argv", ["zhipu_search.py", "测试", "--count", "5"]), patch.object(client, "build_opener") as opener, redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as caught:
                client.main()
        self.assertEqual(caught.exception.code, 2)
        opener.assert_not_called()

    def test_credentials_not_forwarded_to_redirects(self):
        request = object()
        self.assertIsNone(client.NoRedirect().redirect_request(request, None, 302, "", {}, "https://example.org/"))


class CredentialsTests(unittest.TestCase):
    def test_environment_priority_and_file_fallback(self):
        with tempfile.TemporaryDirectory(prefix="zhipu-search-", dir="/tmp") as temp:
            path = Path(temp) / ".env"
            path.write_text("ZHIPU_API_KEY=file-test-key\n", encoding="utf-8")
            with patch.object(client, "ENV_FILE", path), patch.dict(os.environ, {"ZHIPU_API_KEY": "env-test-key"}, clear=True):
                self.assertEqual(client.load_api_key(), "env-test-key")
            with patch.object(client, "ENV_FILE", path), patch.dict(os.environ, {}, clear=True):
                self.assertEqual(client.load_api_key(), "file-test-key")
            with patch.object(client, "ENV_FILE", path.parent / "absent"), patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(client.SearchError) as caught:
                    client.load_api_key()
                self.assertEqual(caught.exception.details["kind"], "missing_credentials")


if __name__ == "__main__":
    unittest.main()
