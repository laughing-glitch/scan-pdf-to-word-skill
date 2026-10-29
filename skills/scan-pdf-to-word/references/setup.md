# 环境准备与故障处理

本文件给执行任务的 AI 阅读。用户安装 Skill 后，可以直接提供 PDF 和转换要求，由 AI 检查并准备运行环境。

## Python

使用宿主已经提供的 Python 3.10+；不要把作者电脑上的绝对路径复制给其他用户。

```text
<Python> <技能目录>/scripts/bootstrap.py
<Python> <技能目录>/scripts/bootstrap.py --install
```

`--install` 只在缺库时创建用户缓存目录下的 venv，并从 PyPI 安装本技能 `requirements.txt` 中的依赖。不要继续使用旧解释器；以脚本返回的 `python` 为准。如果已有宿主环境满足依赖，不做重复安装。

如果机器没有 Python，先检查宿主运行环境。仍没有时，在当前用户授权范围内通过官方安装器/系统包管理器安装；需要系统授权时解释具体组件及用途。不要静默修改全局 PATH、关闭安全软件或反复尝试管理员安装。

## OCR

Mac 的 Vision 需要可运行的 Swift 工具链。`swift` 路径存在并不保证开发工具完整；遇到编译/初始化失败可改用 Tesseract，或直接用宿主读图，不必卡在 Vision。

Tesseract 为可选加速组件，需同时具备程序和对应语言数据。常见位置包括 PATH、Windows `Program Files/Tesseract-OCR`。也可设置 `SCAN_PDF_TO_WORD_TESSERACT` 指向可执行文件。运行 `tesseract --version` 和 `tesseract --list-langs` 验证，不要只检查安装目录。

- macOS：已有 Homebrew 时可使用 `brew install tesseract`。
- Windows：按照 [Tesseract 官方安装说明](https://tesseract-ocr.github.io/tessdoc/Installation.html) 选择其链接的 Windows 安装包，或先查询系统包管理器中的实际包名再安装。
- Linux：使用发行版的 `tesseract-ocr` 软件包。

系统软件安装遵循用户和宿主的权限规则，脚本本身不自动调用管理员安装器。

缺少繁体/简体/英文语言包时，可运行：

```text
<Python> <技能目录>/scripts/bootstrap.py --download-languages
```

仅从 Tesseract 官方 `tessdata_fast` 的固定 `4.1.0` 标签下载 `eng`、`chi_tra`、`chi_sim`，保存到用户缓存，不改系统语言目录。`ocr.py` 会自动发现；自定义缓存时传 `--tessdata`。首次准备需要网络，后续本地 OCR 不需联网。

## Word 渲染

优先用宿主已有的文档渲染器。否则安装 [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/)，使用 `render_docx.py`。该脚本会检查 PATH、Mac 应用目录和 Windows 常见安装目录，也支持 `--soffice` 或 `SCAN_PDF_TO_WORD_SOFFICE`。

每次渲染使用临时 LibreOffice 用户配置，不连接或关闭用户已打开的 Office 文档。完成后查看输出目录中的每张 PNG。仅能打开 DOCX 或提取其 XML，不能替代视觉检查。

## 中文字体与分页

默认 Word 中文字体：Windows 为 SimSun，Mac 为 Songti TC，Linux 为 Noto Serif CJK TC；可以在转录 JSON 中指定。字体必须在实际渲染环境可用，字体替换可能改变分页。

出现方框、空字或异常换行时，先检查字体，而不是更改正文。可使用系统已有中文字体，或从 [Noto CJK 官方项目](https://github.com/notofonts/noto-cjk) 安装合适字体。若宿主使用独立 fontconfig，按其文档设置任务级字体搜索路径，再重新渲染；不要修改用户全局配置来掩盖问题。

## 失败边界

同一个问题尝试两到三种合理方法仍无进展时，保留已经完成的文件，说明卡点、已验证范围和可选路径。不可因缺 OCR 就要求用户手动转录；能读图时继续逐页处理。不可因缺渲染器就宣称排版已通过。
