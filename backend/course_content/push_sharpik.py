import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def main() -> None:
    base = os.environ.get("COURSE_ADMIN_API", "http://127.0.0.1:8000/api/v1").rstrip("/")
    url = f"{base}/course/admin/replace-with-sharpik-course"
    req = urllib.request.Request(
        url,
        method="POST",
        data=b"{}",
        headers={"Content-Type": "application/json"},
    )
    email = (os.environ.get("COURSE_ADMIN_EMAIL") or "").strip()
    password = (os.environ.get("COURSE_ADMIN_PASSWORD") or "").strip()
    handlers: list = []
    if email and password:
        mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        origin = urllib.parse.urljoin(url, "/")
        mgr.add_password(None, origin, email, password)
        handlers.append(urllib.request.HTTPBasicAuthHandler(mgr))
    opener = (
        urllib.request.build_opener(*handlers)
        if handlers
        else urllib.request.build_opener()
    )
    try:
        with opener.open(req, timeout=300) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(resp.status, body)
    except urllib.error.HTTPError as e:
        print(e.code, e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
