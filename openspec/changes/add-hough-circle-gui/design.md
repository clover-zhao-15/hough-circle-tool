## Context

仓库 `hough_circle_tool` 目前只有任务原文、两张验收图和 Git 元数据。已确认的环境事实：

- Python 3.12.3；系统 OpenCV 4.6.0、NumPy 1.26.4 可用。
- WSLg 可用：`DISPLAY=:0`、`WAYLAND_DISPLAY=wayland-0`、`/mnt/wslg` 存在，可在 WSL 内显示 Qt 窗口。
- PySide6 6.12.0 已装入项目 `.venv`；`Noto Sans CJK SC` 已装入 `~/.local/share/fonts`，Qt 实测以 `wayland` 平台启动（1280×800）。
- 用 `HOUGH_GRADIENT` 在两张验收图上实测：硬币图 30 ms/帧，饼干盘图 4.4 ms/帧。
- 验收图：`examples/coins.jpg`（760×385）、`examples/cookie-plate.png`（520×520）。

## Goals / Non-Goals

**Goals:**

- 单窗口完成导入、调参、重新检测、预览与导出标注图。
- 默认参数在两张验收图上稳定得到 2 个硬币外缘与 1 个盘沿，且参数可被评审复现。
- 预览与导出使用同一套标注逻辑，结果一致。

**Non-Goals:**

- 不实现视频、实时相机、ROS 2 节点或 CLI 交付。
- 不做自动参数搜索、批量导出、检测结果持久化。
- 不引入深度学习或自研 Hough 实现。

## Decisions

- **GUI 框架**：PySide6（Qt 6），单 `QMainWindow`，左侧参数表单、中间文件列表、右侧预览 `QLabel`、底部状态栏。替代方案 Tkinter 被否决：中文文本与高 DPI 支持较弱，且题目指定 PySide6。
- **同步检测**：检测在 GUI 线程内直接执行，不引入 `QThread`。实测两张图单帧 ≤30 ms，多选少量图片不会造成可感知卡顿。替代方案（后台线程 + 信号）被否决：当前规模下属于多余复杂度；若后续单帧超过 200 ms 再拆分。
- **单一标注函数**：`detector.annotate()` 返回 BGR 标注图，预览与导出共用，避免两套绘制逻辑产生偏差。
- **参数模型**：`HoughParams` 数据类承载六个参数与固定预处理；默认值 `dp=1.0`、`minDist=200`、`param1=100`、`param2=40`、`minRadius=150`、`maxRadius=300`，已在本机 OpenCV 4.6.0 上逐图验证。
- **预处理固定**：灰度化 + `GaussianBlur(5×5, σ=2)`，不放进界面；README 记录该固定步骤，因为参数复现依赖它。
- **依赖策略**：项目内新建 `.venv --system-site-packages`，复用系统 OpenCV 4.6.0，仅安装 PySide6。替代方案（pip 安装 opencv-python）被否决：版本变化可能改变 `HoughCircles` 结果，破坏已验证的验收参数。
- **图像显示**：`cv2` 的 BGR 转为 RGB 后封装 `QImage`；按窗口尺寸等比缩放，缩放不重新检测。
- **图内文字**：圆半径标签使用 ASCII（`cv2.putText` 不支持中文字形）；界面文字用中文，依赖 `fonts-noto-cjk`，字体缺失时退回英文标签。
- **错误处理**：`cv2.imread` 返回 `None` 或参数非法时在状态栏提示，跳过该图并继续处理其余文件。

## Risks / Trade-offs

- **Qt 平台插件依赖**：WSLg 下 Qt 走 wayland 已实测成功；若强制 xcb，系统缺 `libxcb-cursor0`，需安装或保留 wayland。README 记录 `QT_QPA_PLATFORM` 及实测平台名。
- **中文字体缺失**：已用用户级 `fonts-noto-cjk` 解决；换机器或 CI 需重新安装，否则中文界面显示方框。
- **参数过拟合**：默认参数只保证两张验收图；其他图片误检/漏检由用户调整六个参数解决，界面默认值不代表通用最优。
- **版本敏感**：OpenCV 版本变化可能改变结果。对策：锁定系统 4.6.0，README 记录 `cv2.__version__` 与 Python 版本，测试断言允许 ±10 px 偏差。
- **大图阻塞**：极大图片可能让同步检测超过 200 ms；当前验收图不触发，若出现则后续变更再引入后台线程。
- **导出格式**：`cv2.imwrite` 按扩展名写 PNG/JPEG；JPEG 有损但可接受，默认给 PNG。
