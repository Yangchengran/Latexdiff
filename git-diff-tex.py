import argparse
import subprocess
import tempfile
import shutil
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="单文件 LaTeX 对比工具")
    parser.add_argument("filename", help="要对比的 .tex 文件路径 (例如 main.tex)")
    parser.add_argument("old_commit", help="旧版本的 Commit (例如 HEAD~1)", default="HEAD~1", nargs="?")
    args = parser.parse_args()

    # 获取当前工作目录
    cwd = os.getcwd()
    # 最终输出的 PDF 文件名
    output_pdf = "diff.pdf"

    print(f"👀 正在提取 {args.old_commit} 版本的 {args.filename} ...")

    # 1. 创建临时目录 (用完即焚)
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # 2. 获取旧版本文件内容
        # git show 的语法是: git show commit:filepath
        # 我们把它直接写入临时目录下的 old.tex
        old_file_path = os.path.join(temp_dir, "old.tex")
        try:
            # 这里的 check_output 返回的是 bytes
            content = subprocess.check_output(
                ["git", "show", f"{args.old_commit}:{args.filename}"], 
                cwd=cwd
            )
            with open(old_file_path, "wb") as f:
                f.write(content)
        except subprocess.CalledProcessError:
            print(f"❌ 无法找到文件。请检查 commit hash 或文件名是否正确。")
            sys.exit(1)

        # 3. 运行 latexdiff
        # 对比：临时目录里的 old.tex <---> 你硬盘上当前的 args.filename
        print("📝 正在生成 Diff...")
        diff_tex_path = os.path.join(temp_dir, "diff.tex")
        cmd_diff = f"latexdiff {old_file_path} {os.path.join(cwd, args.filename)} > {diff_tex_path}"
        subprocess.run(cmd_diff, shell=True, check=True)

        # 4. 编译 PDF (关键步骤！)
        print("⚙️  正在编译...")
        
        # 技巧：设置 TEXINPUTS 环境变量
        # 这告诉 pdflatex: "如果在临时目录找不到图片/引用，去原来的目录(cwd)找"
        # 最后的冒号 : 也就是 Linux 下的分隔符，表示“追加标准路径”
        env = os.environ.copy()
        env['TEXINPUTS'] = f".:{cwd}:" 

        compile_cmd = ["pdflatex", "-interaction=nonstopmode", "diff.tex"]
        
        # 运行两次以解决引用
        try:
            subprocess.run(compile_cmd, cwd=temp_dir, env=env, stdout=subprocess.DEVNULL)
            subprocess.run(compile_cmd, cwd=temp_dir, env=env, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("❌ 编译出错")
            sys.exit(1)

        # 5. 把 PDF 拿回来
        generated_pdf = os.path.join(temp_dir, "diff.pdf")
        if os.path.exists(generated_pdf):
            shutil.move(generated_pdf, os.path.join(cwd, output_pdf))
            print(f"✅ 搞定！文件已生成: {output_pdf}")
        else:
            print("❌ 未生成 PDF，可能是 LaTeX 编译错误。")

if __name__ == "__main__":
    main()