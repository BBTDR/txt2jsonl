#!/usr/bin/env python3
import sys
import re
import json
import random
import string
import uuid

def random_string(min_len=5, max_len=100):
    length = random.randint(min_len, max_len)
    chars = string.ascii_letters + string.digits + "_-"
    return ''.join(random.choice(chars) for _ in range(length))

def random_hex(length=32):
    return uuid.uuid4().hex[:length]

def generate_noise_fields():
    categories = ["code", "text", "data", "model", "config", "system", "log", "event", "trace", "metric"]
    sources = ["opensource", "internal", "crawled", "synthetic", "manual", "generated", "imported", "derived"]
    versions = ["EB5", "EB6", "EB7", "V1.0", "V2.1", "ALPHA", "BETA", "RC1", "GA", "STABLE"]
    return [
        {"category": random.choice(categories)},
        {"data_id": random_hex(32)},
        {"examples": [random_string(10, 60) for _ in range(random.randint(0, 3))]},
        {"ignored_key": random_string(0, 80)},
        {"query_source": random.choice(sources)},
        {"schema_version": random.choice(versions)},
    ]

def split_text_to_chunks(text):
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_len = 0
    target_size = random.randint(50, 1000)

    for line in lines:
        line_len = len(line) + 1
        if current_len + line_len > target_size and current_len >= 50:
            chunks.append(current_chunk)
            current_chunk = [line]
            current_len = line_len
            target_size = random.randint(50, 1000)
        else:
            current_chunk.append(line)
            current_len += line_len

    if current_chunk:
        if chunks and current_len < 50:
            chunks[-1].extend(current_chunk)
        else:
            chunks.append(current_chunk)

    return chunks

def parse_chapters(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    chapter_pattern = re.compile(r'^(第[一二三四五六七八九十百千万零\d]+章\s*.*)$', re.MULTILINE)
    matches = list(chapter_pattern.finditer(content))

    if not matches:
        return [{"chapter_id": "全文", "text": content.strip()}]

    chapters = []
    for i, match in enumerate(matches):
        chapter_title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        chapter_text = content[start:end].strip()
        chapters.append({"chapter_id": chapter_title, "text": chapter_text})

    return chapters

def build_jsonl(chapters):
    results = []
    for ch in chapters:
        text_chunks = split_text_to_chunks(ch["text"])
        content_items = []
        for i, chunk in enumerate(text_chunks):
            content_items.append({"text": chunk})
            if i < len(text_chunks) - 1:
                noise = generate_noise_fields()
                for field in noise:
                    content_items.append(field)
        record = {
            "chapter_id": ch["chapter_id"],
            "content": content_items
        }
        results.append(json.dumps(record, ensure_ascii=False))
    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python3 txt2jsonl.py <txt文件路径>")
        sys.exit(1)

    filepath = sys.argv[1]
    chapters = parse_chapters(filepath)
    lines = build_jsonl(chapters)

    output_path = "log.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

    print(f"已生成: {output_path} ({len(lines)} 个章节)")

if __name__ == "__main__":
    main()
