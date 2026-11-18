# Tasks

## 1. 环境与规格

- [x] 1.1 在项目根目录创建 `.venv`（`--system-site-packages`）并安装 PySide6，验证方式：`python -c "import PySide6, cv2, numpy; print(PySide6.__version__, cv2.__version__, numpy.__version__)"`。
- [x] 1.2 将 Python、OpenCV、NumPy、PySide6 版本记入 `docs/measurement.md`（README 环境说明在 5.1 同步）。
- [x] 1.3 校验 OpenSpec 四份工件，验证方式：`openspec validate add-hough-circle-gui --strict` 通过。

## 2. 检测核心

- [x] 2.1 实现 `params.py`：`HoughParams` 默认值、范围校验、半径顺序校验，验证方式：`pytest tests/test_params.py`。
- [x] 2.2 实现 `detector.py` 的 `detect_circles()`：灰度化、`GaussianBlur(5×5, σ=2)`、`HOUGH_GRADIENT`，验证方式：`pytest tests/test_detector.py`。
- [x] 2.3 实现 `annotate()`：绘制圆轮廓、圆心、半径文本，验证方式：合成圆图断言像素变化与圆数量。
- [x] 2.4 用默认参数对两张验收图断言圆数量、圆心与半径（±10 px），验证方式：`pytest tests/test_detector.py -q`。

## 3. 图形界面

- [x] 3.1 实现 `app.py` 与入口 `python -m hough_circle_tool`，验证方式：WSLg 中窗口能启动并正常退出。
- [x] 3.2 实现 `main_window.py` 布局：工具栏、参数表单、文件列表、预览区、状态栏。
- [x] 3.3 接入文件对话框多选、去重、不可读文件跳过，验证方式：选择两张验收图后列表出现两项。
- [x] 3.4 接入六个参数控件与“重新检测”按钮，验证方式：修改 `param2` 后结果数量变化，非法半径范围被拒绝。
- [x] 3.5 接入预览：等比缩放、圆标注、数量与耗时显示，验证方式：硬币图显示 2 个圆。
- [x] 3.6 接入导出对话框与编码保存，验证方式：导出 PNG 后重新打开，标注与预览一致。
- [x] 3.7 状态栏错误处理与中文界面验证，验证方式：中文字体安装后中文正常显示；不可读文件只报错不崩溃。

## 4. 验收

- [x] 4.1 在 WSLg 中打开 `examples/coins.jpg`，确认检出 2 个硬币外缘，验证方式：截图或状态栏数量。
- [x] 4.2 在 WSLg 中打开 `examples/cookie-plate.png`，确认检出 1 个盘沿。
- [x] 4.3 导出标注图到 `docs/acceptance/coins_annotated.png` 与 `docs/acceptance/cookie-plate_annotated.png`。
- [x] 4.4 运行 `pytest -q`，全部通过。

## 5. 文档与提交

- [x] 5.1 README 写明启动方式、环境版本、两张图的六参数与标注图。
- [x] 5.2 `docs/measurement.md` 记录实测命令、输出与参数表。
- [x] 5.3 按约定提交，验证方式：`git log --format='%an <%ae> %s'` 显示 `clover-zhao-15 <332112843+clover-zhao-15@users.noreply.github.com>`。

## 验证记录

### 环境（2026-11-18）

```text
$ .venv/bin/python -c "import PySide6, cv2, numpy; print(PySide6.__version__, cv2.__version__, numpy.__version__)"
6.12.0 4.6.0 1.26.4

$ openspec validate add-hough-circle-gui --strict
Change 'add-hough-circle-gui' is valid

$ .venv/bin/python -c "from PySide6.QtWidgets import QApplication; app=QApplication([]); print(app.platformName(), app.primaryScreen().size())"
wayland PySide6.QtCore.QSize(1280, 800)
```

### 实施与验收（2026-11-18）

```text
$ pytest -q
11 passed in 0.37s

$ .venv/bin/python -m hough_circle_tool
coins.jpg: 2 circles -> [Circle(x=568, y=192, radius=180),
                         Circle(x=192, y=190, radius=178)] | 46.5 ms
export: docs/acceptance/coins_annotated.png True
cookie-plate.png: 1 circles -> [Circle(x=264, y=258, radius=244)] | 8.4 ms
export: docs/acceptance/cookie-plate_annotated.png True

# 重复路径只加入一次；缺失文件提示后继续；minRadius > maxRadius 被拒绝
duplicate add: [PosixPath('/home/zhaoxuejiang/rt_vision/hough_circle_tool/examples/coins.jpg')]
list count: 1
missing add: []
status: 无法读取: missing.png
invalid params rejected: minRadius 不能大于 maxRadius
```

## Workflow follow-up

- 组长确认实现与验收后，归档该变更并同步主规格。
