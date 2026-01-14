import argparse
import subprocess
import tempfile
import shutil
import os
import sys

def run_command(cmd, cwd=None, capture_output=False):
    """
    辅助函数：运行 shell 命令
    """
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            check=True, 
            shell=True, # 允许使用 shell 特性如管道
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {cmd}")
        if capture_output:
            print(e.stderr.decode())
        sys.exit(1)

def main():
    # 1. 解析参数
    parser = argparse.ArgumentParser(description="Git LaTeX Diff 工具 - 自动对比并清理中间文件")
    parser.add_argument("old_commit", help="旧版本的 Commit Hash 或 Tag (例如: HEAD~1)")
    parser.add_argument("new_commit", help="新版本的 Commit Hash 或 Tag (例如: HEAD)", nargs='?', default="HEAD")
    parser.add_argument("--main", help="主 tex 文件名 (默认: main.tex)", default="main.tex")
    parser.add_argument("--out", help="输出文件名 (默认: diff.pdf)", default="diff.pdf")
    
    args = parser.parse_args()

    # 获取绝对路径，防止在临时目录里迷路
    original_cwd = os.getcwd()
    output_pdf_path = os.path.join(original_cwd, args.out)

    print(f"🚀 正在准备对比: {args.old_commit} <-> {args.new_commit}")

    # 2. 创建临时目录沙盒 (Context Manager 确保自动清理)
    # 这一行代码是核心：with 语句块结束时，temp_dir 会被自动删除，无论是否报错
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📂 创建临时工作区: {temp_dir}")
        
        dir_old = os.path.join(temp_dir, "old")
        dir_new = os.path.join(temp_dir, "new")
        os.makedirs(dir_old)
        os.makedirs(dir_new)

        # 3. 提取文件 (使用 git archive 避免脏文件)
        print("📦 正在提取旧版本代码...")
        run_command(f"git archive {args.old_commit} | tar -x -C {dir_old}", cwd=original_cwd)
        
        print("📦 正在提取新版本代码...")
        run_command(f"git archive {args.new_commit} | tar -x -C {dir_new}", cwd=original_cwd)

        # 4. 运行 latexdiff
        # --flatten 选项很重要，它可以处理 \input 和 \include 的多文件情况
        diff_tex_path = os.path.join(temp_dir, "diff.tex")
        print("📝 正在生成 Diff TeX 源码 (可能需要一点时间)...")
        
        # 这里的关键是把 old 和 new 目录传给 latexdiff
        cmd_diff = f"latexdiff --flatten {os.path.join(dir_old, args.main)} {os.path.join(dir_new, args.main)} > {diff_tex_path}"
        run_command(cmd_diff)

        # 5. 编译 PDF
        # 我们进入 temp_dir 编译，这样 .aux .log 全都会留在 temp_dir 里，不会污染你的项目目录
        print("⚙️  正在编译 PDF (pdflatex)...")
        
        # 通常跑两次以修正引用，-interaction=nonstopmode 防止报错卡死
        compile_cmd = f"pdflatex -interaction=nonstopmode diff.tex"
        
        try:
            # 第一次编译
            run_command(compile_cmd, cwd=temp_dir, capture_output=True)
            # 第二次编译 (为了引用)
            run_command(compile_cmd, cwd=temp_dir, capture_output=True)
        except SystemExit:
            print("❌ 编译失败，请检查 LaTeX 语法错误。")
            # 只有出错时，为了调试，我们可能想把 diff.tex 拷出来看看
            shutil.copy(diff_tex_path, os.path.join(original_cwd, "debug_diff.tex"))
            print(f"⚠️  已将中间文件保存为 debug_diff.tex 供调试")
            sys.exit(1)

        # 6. 取回结果
        generated_pdf = os.path.join(temp_dir, "diff.pdf")
        if os.path.exists(generated_pdf):
            shutil.move(generated_pdf, output_pdf_path)
            print(f"✅ 成功！文件已生成: {args.out}")
        else:
            print("❌ 未找到生成的 PDF 文件。")

    # 离开 with 块，temp_dir 在这里自动“灰飞烟灭”，无需手动 rm

if __name__ == "__main__":
    main()