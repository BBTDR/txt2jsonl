# txt2jsonl

将 TXT 小说/书籍文件转换为结构化 JSONL 格式，自动识别章节并按章节拆分，适用于数据处理、模型训练数据准备等场景。

## 功能

- 自动识别章节标题（支持 `第X章`、`第一章` 等中文数字和阿拉伯数字格式）
- 每个章节输出为一行 JSON（标准 JSONL 格式）
- 正文按行随机分段为多个 `text` 字段（50~1000字/段）
- `text` 字段之间穿插6个噪声字段，模拟真实数据集结构
- 输出文件为合法 JSONL，可被标准 JSON 解析器正确读取

## 使用方法

```bash
python3 txt2jsonl.py <txt文件路径>
```

执行后在当前目录生成 `log.jsonl`。

### 示例

```bash
python3 txt2jsonl.py ~/books/novel.txt
```

## 输出格式

每行一个 JSON 对象，结构如下：

```json
{
  "chapter_id": "第一章 船长的日记",
  "content": [
    {"text": ["第一行正文", "第二行正文", "第三行正文..."]},
    {"category": "code"},
    {"data_id": "3e3ae6aa282111f1aef8043f72be3cc6"},
    {"examples": ["random_string"]},
    {"ignored_key": "some_value"},
    {"query_source": "opensource"},
    {"schema_version": "EB5"},
    {"text": ["下一段第一行", "下一段第二行..."]},
    ...
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `chapter_id` | string | 章节标题，如 "第一章 船长的日记" |
| `content` | array | 内容数组，包含 text 字段和噪声字段交替排列 |
| `content[].text` | array of string | 正文内容，每个元素为一行原文（保留原始换行） |

### 噪声字段（穿插在 text 之间）

每两个 `text` 字段之间固定插入以下6个噪声字段，值为随机生成：

| 字段 | 值类型 | 示例 |
|------|--------|------|
| `category` | string | "code", "text", "data", "model" 等 |
| `data_id` | string | 32位十六进制 UUID |
| `examples` | array | 0~3个随机字符串 |
| `ignored_key` | string | 随机字符串（0~80字符） |
| `query_source` | string | "opensource", "internal", "crawled" 等 |
| `schema_version` | string | "EB5", "V1.0", "ALPHA" 等 |

## 章节识别规则

脚本通过正则表达式识别章节标题：

```
第[一二三四五六七八九十百千万零\d]+章\s*.*
```

支持的格式示例：
- `第一章 标题`
- `第1章 标题`
- `第一千一百三十章 标题`
- `第100章`（无标题也可识别）

### 边界情况

- **无章节标识**：如果全文没有匹配到任何章节标题，整篇文档作为一个 JSON 输出，`chapter_id` 为 `"全文"`
- **章节前的内容**（如书名、简介等）：不会被包含在输出中，仅从第一个章节开始
- **空行**：会被保留在 text 数组中作为空字符串元素
- **特殊字符**：JSON 序列化会自动转义双引号、反斜杠等特殊字符
- **大文件**：逐章节处理，内存占用与单章节大小相关，非全文加载

## text 分段规则

- 按行边界切分，不会在一行文本中间截断
- 每个 text 字段包含的文本总量在 50~1000 字之间（随机）
- 如果剩余内容不足 50 字，会合并到前一个 text 字段中
- 最后一个 text 字段之后不插入噪声字段

## 依赖

- Python 3.6+
- 无第三方依赖（仅使用标准库）

## 注意事项

1. 输入文件编码必须为 UTF-8
2. 输出文件固定命名为 `log.jsonl`，会覆盖已有文件
3. 噪声字段的值每次运行随机生成，同一文件多次转换结果不同
4. text 字段的分段大小也是随机的，每次运行结果不完全一致

## License

MIT
