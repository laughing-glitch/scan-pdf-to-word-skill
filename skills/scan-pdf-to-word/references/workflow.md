# 命令与验收

这些是给 AI 执行的命令，不是要求用户手动逐条敲。所有路径都要按当前系统正确引用；Windows PowerShell 调用带空格的可执行文件时使用 `& "路径"`。下面的 `<Python>` 和 `<技能目录>` 需替换成已经确认的实际路径。

```text
<Python> <技能目录>/scripts/pdf_pages.py input.pdf --out work/source --dpi 300
<Python> <技能目录>/scripts/ocr.py work/source/manifest.json --out work/ocr --engine auto
```

默认 OCR 是繁体＋英文。简体 Tesseract 加 `--languages chi_sim+eng`；简体 Vision 加 `--vision-languages zh-Hans,en-US`。需要第二识别结果时另用新输出目录：

```text
<Python> <技能目录>/scripts/ocr.py work/source/manifest.json --out work/ocr-second --engine tesseract
```

页图编号对应原 PDF 的 1-based 页码。`--pages 2,4-6` 只在用户要求子集或明确进行抽样验证时使用。文本层字符数只是路由线索，不是可信度。

打开每张源页图，将 OCR 草稿校对成 `work/transcript.json`。不要把 OCR 文本未经检查直接灌入最终 Word。尤其留意：繁简混转、同形字、人名、数字、重复/丢失的“的”、空白栏、公式和表格合并。

```text
<Python> <技能目录>/scripts/build_docx.py work/transcript.json --out output/editable-v1.docx
<Python> <技能目录>/scripts/check_docx.py output/editable-v1.docx --transcript work/transcript.json --report work/check-v1.json
<Python> <技能目录>/scripts/render_docx.py output/editable-v1.docx --out work/render-v1
<Python> <技能目录>/scripts/check_docx.py output/editable-v1.docx --transcript work/transcript.json --rendered-pdf work/render-v1/editable-v1.pdf --report work/check-render-v1.json
```

使用宿主内置渲染器时，以它实际生成的 PDF 路径替代上例。中间预览和检查文件放在工作目录，最终交付以 Word 为主。

`check_docx.py` 会检查：

- 按源页比较转录 JSON 和 DOCX 的原生文字，忽略空白差异，保留字符和标点差异。
- 批注开始/结束/引用是否匹配。
- 原生表格、图片、文本框数量。
- 在临时副本中修改正文和单元格、保存再读回，原文件不变。
- 提供渲染 PDF 时核对页数。

它**不会**判断转录 JSON 是否忠实原稿，也不会判断文字是否遮挡。最后逐页查看源图与渲染图，在工作记录中填写真实完成状态。

验收至少覆盖：全部要求的源页有对应内容；文字与表格可编辑；题目/选项/空白完整；无明显缺字、截断或重叠；疑点有批注；图片保留范围明确。用户要求每源页对应一页时，保持 `preserve_page_count: true`；允许重新流排时可以设为 `false` 并解释页数变化。
