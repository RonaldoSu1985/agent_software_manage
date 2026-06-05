import os
import glob

# 构建输出目录
dist_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
output_dir = os.path.join(os.path.dirname(__file__), "deployment_package", "frontend")

# 读取文件
with open(os.path.join(dist_dir, "index.html"), "r", encoding="utf-8") as f:
    html_content = f.read()

# 动态查找 JS 和 CSS 文件
js_files = glob.glob(os.path.join(dist_dir, "assets", "index-*.js"))
css_files = glob.glob(os.path.join(dist_dir, "assets", "index-*.css"))

if not js_files:
    raise Exception("No JS file found in assets directory")
if not css_files:
    raise Exception("No CSS file found in assets directory")

js_file = js_files[0]
css_file = css_files[0]

with open(js_file, "r", encoding="utf-8") as f:
    js_content = f.read()

with open(css_file, "r", encoding="utf-8") as f:
    css_content = f.read()

# 获取文件名用于替换
js_filename = os.path.basename(js_file)
css_filename = os.path.basename(css_file)

# 替换为内嵌内容
html_content = html_content.replace(
    f'<script type="module" crossorigin src="/assets/{js_filename}"></script>',
    f'<script type="module">{js_content}</script>'
)

html_content = html_content.replace(
    f'<link rel="stylesheet" crossorigin href="/assets/{css_filename}">',
    f'<style>{css_content}</style>'
)

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 写入输出文件
with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

# 复制其他文件
import shutil
for file in ["favicon.svg", "icons.svg"]:
    src = os.path.join(dist_dir, file)
    dst = os.path.join(output_dir, file)
    if os.path.exists(src):
        shutil.copy(src, dst)

print(f"Successfully inline assets into index.html")
print(f"JS file: {js_filename}")
print(f"CSS file: {css_filename}")
print(f"Output directory: {output_dir}")