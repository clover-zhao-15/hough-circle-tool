# 项目约定

这是一个 PySide6 + OpenCV 的桌面端霍夫圆检测工具。一次工作分支只解决对应的 OpenSpec 变更，保持 `python -m hough_circle_tool` 启动方式可用。

开始实施前，阅读 `openspec/changes/add-hough-circle-gui/` 中的四份工件，确认规格与验收场景；遇到会改变外部行为的歧义，先向需求方确认。

- 入口：`source .venv/bin/activate && python -m hough_circle_tool`
- 测试：`pytest`
- 验收图：`examples/coins.jpg` 必须检出 2 个硬币外缘；`examples/cookie-plate.png` 必须检出 1 个盘沿。
- 验收参数：两张图默认使用 `dp=1`、`minDist=200`、`param1=100`、`param2=40`、`minRadius=150`、`maxRadius=300`，预处理为灰度 + `GaussianBlur(5×5, σ=2)`；改参数必须同步更新 README 与 `docs/measurement.md`。
- 环境：Ubuntu 24.04 WSL2 + WSLg；venv 使用 `--system-site-packages` 复用系统 OpenCV，仅额外安装 PySide6。
- 提交：`<type>: <short description>`，type 取 feat/fix/refactor/docs/chore/test/build。
