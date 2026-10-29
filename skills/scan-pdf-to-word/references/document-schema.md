# 校对转录 JSON v1

JSON 是经过原图核对的中间稿，不是 OCR 自动识别准确的证明。不要在文本中放执行指令。

```json
{
  "schema_version": 1,
  "document": {
    "title": "工作紙",
    "language": "zh-TW",
    "font_size_pt": 12,
    "page_size_cm": [21, 29.7],
    "margins_cm": [1.8, 1.8, 1.8, 1.8],
    "preserve_page_count": true,
    "header": "工作紙",
    "footer": ""
  },
  "pages": [
    {
      "source_page": 1,
      "blocks": [
        {"type": "paragraph", "text": "練習一", "size_pt": 18, "bold": true, "keep_with_next": true},
        {"type": "paragraph", "text": [{"text": "原稿疑字", "underline": true, "comment": "原件此處不清晰，請核對紙本。"}]},
        {"type": "table", "widths_cm": [4, 13.4], "rows": [["題目", "回答"], ["姓名", ""]], "header_rows": 1}
      ]
    }
  ]
}
```

页面按 `source_page` 排序且不可重复。每个页面必须有 `blocks`，明确的空白页可放一个空段落。相邻源页之间生成硬分页；页内容过多仍可能自动溢出，必须渲染检查。

## 段落

`type: paragraph`，`text` 可为普通字符串或 run 列表。不会把 `<u>` 等文本当作 HTML 执行/解释。

段落可选：`size_pt`、`bold`、`align`（left/center/right/justify）、`style`（例如 Heading 1）、`space_after_pt`、`line_spacing_pt`、`keep_with_next`、`keep_together`、`left_indent_cm`、`first_line_indent_cm`。

run 可选：`bold`、`italic`、`underline`、`size_pt`、`comment`。批注直接锚定该 run，避免同一句多次出现时误挂到别页。锚定文字必须非空；正文保留源字，解释放在 comment。

选择题可用一个题干段落加一个选项段落，或无边框表格排选项。不要自动选择答案。

## 表格、答题框

`type: table`，必需 `widths_cm` 和矩形 `rows`。每个 cell 可为字符串、run 列表，或 `{"paragraphs": [{"text": "…"}, ...]}`。总宽度不应超过可用版心。

可选：`size_pt`、`border`（single/dotted/nil）、`header_rows`、`min_row_heights_cm`、`merges`。

`merges` 使用从 0 开始的 `[首行, 首列, 末行, 末列]`，内容全部放在左上角，其他被合并格留空。拒绝重叠或越界合并。行高是最小值，可随用户输入增长。

答题留白用空单元格；需要字格时将相邻小单元格边框设为 dotted。下划线可按原文使用下划线字符或有下划线的 run。内容和栏位都必须可继续编辑。

## 局部图片

```json
{"type": "image", "path": "source/page-0002.png", "crop": [0.1, 0.2, 0.4, 0.5], "width_cm": 5, "purpose": "illustration", "alt": "原件插图"}
```

图片相对转录 JSON 所在目录解析。`crop` 是 `[左, 上, 右, 下]` 的 0–1 相对坐标；可省略。`purpose` 必须为 illustration、handwriting 或 diagram，可另加 `caption`、`align`。它明确保留原图内容，不能把整页扫描图伪装成已转换的正文。

## 字体

`document.font_east_asia` 可指定已安装中文字体；未指定时按操作系统选择。字体、页边距及行距由源文和编辑需求决定，不要硬套示例参数。需要复杂嵌套表格或不同分节时可以扩展生成代码，并重新执行内容与视觉检查。
