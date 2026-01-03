import json
import urllib.request
import socket
import tomllib


def estimate_token(file_path: str) -> int:
    with open("settings.toml", "rb") as f:
        settings = tomllib.load(f)
    api_key = settings.get("user", {}).get("MOONSHOT_API_KEY", "")
    timeout = settings.get("user", {}).get("moonshot_timeout", 3)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    data = {
        "model": "kimi-k2-turbo-preview",
        "messages": [{"role": "user", "content": content}],
    }

    try:
        req = urllib.request.Request(
            "https://api.moonshot.cn/v1/tokenizers/estimate-token-count",
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("data", {}).get("total_tokens", 0)
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
    except TimeoutError as e:
        print(f"TimeoutError: {e}")
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
