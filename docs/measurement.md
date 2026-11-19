# 测量与验收记录

## 环境

| 项 | 值 |
|---|---|
| Python | 3.12.3 |
| OpenCV (`cv2.__version__`) | 4.6.0 |
| NumPy | 1.26.4 |
| PySide6 | 6.12.0 |
| Qt 平台 | `wayland`（WSLg，屏幕 1280×800） |
| 系统 | Ubuntu 24.04，WSL2 内核 6.18.58.1 |
| 中文字体 | Noto Sans CJK SC（用户级 `~/.local/share/fonts`） |

## 验收参数

预处理固定为灰度化 + `GaussianBlur(5×5, σ=2)`，检测方法 `HOUGH_GRADIENT`。

| 图片 | dp | minDist | param1 | param2 | minRadius | maxRadius | 结果 |
|---|---|---|---|---|---|---|---|
| `examples/coins.jpg` | 1 | 200 | 100 | 40 | 150 | 300 | 2 个圆：`(568,192,r180)`、`(192,190,r178)` |
| `examples/cookie-plate.png` | 1 | 200 | 100 | 40 | 150 | 300 | 1 个圆：`(264,258,r244)` |

## 实现前参数核验

```text
$ .venv/bin/python - <<'EOF'
import cv2, numpy as np
def run(path, dp=1, md=200, p1=100, p2=40, rmin=150, rmax=300, blur=5):
    im = cv2.imread(path)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (blur, blur), 2)
    c = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, dp, md,
                         param1=p1, param2=p2, minRadius=rmin, maxRadius=rmax)
    return [] if c is None else np.round(c[0]).astype(int).tolist()
for f in ("examples/coins.jpg", "examples/cookie-plate.png"):
    print(f, '->', run(f))
EOF
examples/coins.jpg -> [[568, 192, 180], [192, 190, 178]]
examples/cookie-plate.png -> [[264, 258, 244]]
```

单帧耗时：硬币图 30.3 ms，饼干盘图 4.4 ms（连续 10 次取平均）。

## GUI 冒烟测试

```text
$ .venv/bin/python - <<'EOF'
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QFontDatabase
app = QApplication([])
print(app.platformName(), app.primaryScreen().size())
w = QLabel('中文界面测试：霍夫圆检测'); w.show(); w.close()
print([f for f in QFontDatabase.families() if 'CJK' in f][:2])
EOF
wayland PySide6.QtCore.QSize(1280, 800)
['Noto Sans CJK HK', 'Noto Sans CJK JP']
```

## GUI 验收（2026-11-18）

```text
$ .venv/bin/python -m hough_circle_tool
# WSLg 中窗口正常显示，Qt 平台 wayland

coins.jpg: 2 circles -> [Circle(x=568, y=192, radius=180),
                         Circle(x=192, y=190, radius=178)] | 46.5 ms
export: docs/acceptance/coins_annotated.png True

cookie-plate.png: 1 circles -> [Circle(x=264, y=258, radius=244)] | 8.4 ms
export: docs/acceptance/cookie-plate_annotated.png True
```

标注图尺寸与输入一致：硬币图 760×385，饼干盘图 520×520。

## 边界行为

```text
$ .venv/bin/python - <<'EOF'   # 重复路径、缺失文件、非法半径
duplicate add: [PosixPath('.../examples/coins.jpg')]
list count: 1
missing add: []
status: 无法读取: missing.png
invalid params rejected: minRadius 不能大于 maxRadius
param2 spin change ok: 30
EOF
```

## 自动化测试

```text
$ pytest -q
...........                                                              [100%]
11 passed in 0.37s
```
