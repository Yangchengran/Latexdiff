# LaTeX Diff Tool

这是一个用于生成 LaTeX 文件版本差异的工具。它结合 Git 和 latexdiff 来创建可视化的 PDF 差异报告。

## 功能特性

- 支持比较两个 Git commit 之间的 LaTeX 文件差异。
- 支持比较 Git commit 与当前工作区文件的差异。
- 自动生成带标记的 diff.tex 文件，并编译为 PDF。
- 处理 LaTeX 文件中的图片引用，确保编译时能找到资源。

## 安装

1. 确保系统已安装以下依赖：
   - Python 3.13 或更高版本
   - Git
   - latexdiff (LaTeX 差异工具)
   - pdflatex (用于编译 PDF)

2. 克隆此仓库：
   ```bash
   git clone <repository-url>
   cd latexdiff
   ```

3. 安装 Python 依赖（如果有）：
   ```bash
   pip install -e .
   ```

## 使用方法

运行 `git-diff-tex` 脚本：

```bash
python git-diff-tex <filename> [old_commit] [new_commit]
```

### 参数说明

- `filename`: 要比较的 LaTeX 文件名，例如 `main.tex`。
- `old_commit`: 旧版本的 Git commit（可选，默认 `HEAD~1`）。
- `new_commit`: 新版本的 Git commit（可选，如果不提供，则与当前工作区文件比较）。

### 示例

1. 比较 `HEAD~1` 与当前工作区文件：
   ```bash
   python git-diff-tex tests/main.tex
   ```

2. 比较两个特定 commit：
   ```bash
   python git-diff-tex tests/main.tex HEAD~2 HEAD
   ```

运行后，会在当前目录生成 `diff.pdf` 文件，显示差异。

## 项目结构

- `main.py`: 示例 Python 脚本。
- `git-diff-tex`: 主脚本，用于生成 LaTeX 差异。
- `tests/main.tex`: 示例 LaTeX 文件。
- `pyproject.toml`: 项目配置。

## 注意事项

- 确保在 Git 仓库中运行此工具。
- 如果 LaTeX 文件包含外部引用（如图片），确保它们在当前目录或 TEXINPUTS 路径中可用。
- 如果编译失败，检查 LaTeX 语法和依赖。

## 许可证

[添加许可证信息，如果有的话]