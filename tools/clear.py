import re


def clear(input_url: str, output_url: str) -> None:
    with open(input_url, "r", encoding="utf-8") as f:
        content = f.read()

    cleared = "<!-- Automatically deleted HTML comments. -->\n\n" + re.sub(
        r"<!--.*?-->", "", content, flags=re.DOTALL
    )

    with open(output_url, "w", encoding="utf-8") as f:
        f.write(cleared)
