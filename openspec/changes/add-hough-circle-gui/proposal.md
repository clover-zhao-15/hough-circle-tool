## Why

任务三要求一个带图形界面的霍夫圆检测工具：导入图片、调参、预览检测结果、导出标注图，并用硬币图与饼干盘图验收。当前仓库只有任务原文与两张验收图，没有任何实现，需要先固定规格、验收口径与实施边界，避免把桌面工具做成 ROS 2 包或 CLI。

## What Changes

- 新增 PySide6 桌面应用，入口为 `python -m hough_circle_tool`，单窗口完成导入、调参、预览与导出。
- 导入：系统文件对话框多选 JPG/JPEG/PNG/BMP，可多次追加同一批或不同批文件。
- 调参：界面暴露 `dp`、`minDist`、`param1`、`param2`、`minRadius`、`maxRadius`；参数修改后由用户显式触发重新检测。
- 预览：显示当前图片的标注结果（圆轮廓、圆心、半径文本）与检出数量。
- 导出：将当前标注图保存为 PNG 或 JPEG，默认文件名为 `<原文件名>_annotated.png`。
- 验收：`examples/coins.jpg` 检出 2 个硬币外缘，`examples/cookie-plate.png` 检出 1 个盘沿；两图实际参数与标注结果图写入 README 与 `docs/measurement.md`。

## Capabilities

### New Capabilities

- `hough-circle-tool`: 桌面端霍夫圆检测工具，覆盖图片导入、六参数调整、结果预览、标注导出与两张验收图的固定验收口径。

### Modified Capabilities

无。

## Impact

- 代码：新增 `src/hough_circle_tool/`、`tests/`，以及 `docs/acceptance/` 下的标注结果图。
- 依赖：新增 PySide6；OpenCV 4.6.0 与 NumPy 1.26.4 沿用系统包（venv 以 `--system-site-packages` 创建）。
- 运行环境：Ubuntu 24.04 WSL2 + WSLg；README 必须记录 Python 与 `cv2.__version__`，保证评审可复现。
- 非目标：视频、实时相机、ROS 2 包、CLI 交付形态；自研圆检测算法；批量导出全部图片。
- 基线：空仓库 `main`（0 commit）；工作分支 `feat/hough-circle-gui`；GitHub 远端由用户建仓后提供。
