import os


def combine(output_url: str, input_urls: list[str]) -> None:
    base_name = os.path.splitext(os.path.basename(output_url))[0]
    parts = [f'<?xml version="1.0" encoding="UTF-8"?><root id="{base_name}">']

    for url in input_urls:
        with open(url, "r", encoding="utf-8") as f:
            content = f.read()

        # 替换 CDATA 结束标记 ]]>
        content = content.replace("]]>", "]]]]><![CDATA[>")
        parts.append(f'<content id="{url}"><![CDATA[{content}]]></content>')

    parts.append("</root>")

    os.makedirs(os.path.dirname(output_url), exist_ok=True)
    with open(output_url, "w", encoding="utf-8") as f:
        f.write("".join(parts))
