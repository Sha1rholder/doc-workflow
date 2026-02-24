def tokenizer_add1(
    tokenizer_endpoint: str, file_path: str, MOONSHOT_API_KEY: str, moonshot_timeout=3
) -> int:
    import json
    import urllib.request
    import urllib.error
    import socket

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    data = {
        "model": "kimi-k2.5",
        "messages": [{"role": "user", "content": content}],
    }

    try:
        req = urllib.request.Request(
            tokenizer_endpoint,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MOONSHOT_API_KEY}",
            },
        )
        with urllib.request.urlopen(req, timeout=moonshot_timeout) as response:
            result = (
                json.loads(response.read().decode("utf-8"))
                .get("data", {})
                .get("total_tokens", 0)
            )
            print(file_path, "tokens:", result)
            return result + 1
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e}")
        return 0
    except urllib.error.URLError as e:
        print(f"URLError: {e}")
        return 0
    except socket.timeout as e:
        print(f"socket.timeout: {e}")
        return 0
    except ConnectionError as e:
        print(f"ConnectionError: {e}")
        return 0
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return 0
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        return 0
    except OSError as e:
        print(f"OSError: {e}")
        return 0
    except Exception as e:
        print(f"Exception: {e}")
        return 0
