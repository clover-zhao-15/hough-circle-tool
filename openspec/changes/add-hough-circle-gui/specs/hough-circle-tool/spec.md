# Spec Delta

## Purpose

规定桌面端霍夫圆检测工具的图片导入、参数调整、结果预览、标注导出与两张验收图的固定口径，使评审可以按 README 记录的参数复现检测结果。

## ADDED Requirements

### Requirement: 图片导入

工具 SHALL 通过系统文件对话框一次选择一张或多张本地图片，支持 JPG、JPEG、PNG、BMP。已加入列表的相同路径 MUST NOT 重复加入。无法解码的文件 SHALL 被跳过并在状态栏说明，其余文件 MUST 继续处理。

#### Scenario: 多选导入

- **WHEN** 用户在文件对话框中同时选择 `examples/coins.jpg` 与 `examples/cookie-plate.png`
- **THEN** 两张图都出现在文件列表中，并各自显示检出数量

#### Scenario: 不可读文件

- **WHEN** 用户选择的文件中有一个无法解码
- **THEN** 状态栏提示该文件读取失败，其余图片仍完成检测

### Requirement: 参数调整与重新检测

界面 SHALL 提供 `dp`、`minDist`、`param1`、`param2`、`minRadius`、`maxRadius` 六个可编辑参数，默认值 MUST 为 `dp=1.0`、`minDist=200`、`param1=100`、`param2=40`、`minRadius=150`、`maxRadius=300`。检测 MUST 使用界面当前参数，参数被修改后 MUST 由用户显式触发重新检测。当 `minRadius` 大于 `maxRadius` 时，工具 MUST 拒绝检测并提示错误。

固定预处理 MUST 为灰度化后执行 `GaussianBlur(5×5, σ=2)`，并 MUST 记录在 README 中。

#### Scenario: 默认参数

- **WHEN** 用户未修改参数，打开 `examples/coins.jpg`
- **THEN** 检出 2 个圆

#### Scenario: 非法半径范围

- **WHEN** 用户把 `minRadius` 设为大于 `maxRadius` 的值并点击重新检测
- **THEN** 工具不执行检测，状态栏提示半径范围非法

### Requirement: 结果预览

工具 SHALL 显示当前选中图片及其标注结果：每个检出圆 MUST 绘制轮廓、圆心和半径文本，界面 SHALL 显示当前图片的检出数量。预览缩放 MUST NOT 改变检出数据。

#### Scenario: 硬币图预览

- **WHEN** 使用默认参数选中 `examples/coins.jpg`
- **THEN** 预览中两个硬币外缘各有一个圆，状态栏显示 `2`

### Requirement: 标注图导出

工具 SHALL 允许将当前图片的标注结果保存为 PNG 或 JPEG，默认文件名为 `<原文件名>_annotated.png`，且保存内容 MUST 与预览中的标注一致。保存失败时 MUST 给出错误提示且不退出程序。

#### Scenario: 导出硬币图

- **WHEN** 用户对已检出 2 个圆的 `examples/coins.jpg` 执行导出并选择 PNG
- **THEN** 生成的图片包含同样的 2 个圆轮廓、圆心与半径文本

### Requirement: 验收口径与参数记录

使用默认参数时，`examples/coins.jpg` MUST 恰好检出 2 个圆，`examples/cookie-plate.png` MUST 恰好检出 1 个圆；圆心与半径允许 ±10 px 偏差。README MUST 写明启动方式、Python 与 `cv2.__version__`、两张图各自的六参数取值，并嵌入两张标注结果图；`docs/measurement.md` MUST 记录实测命令与输出。

#### Scenario: 硬币图验收

- **WHEN** 使用默认参数运行检测
- **THEN** `coins.jpg` 得到 2 个圆，圆心与半径约为 `(568,192,180)`、`(192,190,178)`，误差不超过 10 px

#### Scenario: 饼干盘图验收

- **WHEN** 使用默认参数运行检测
- **THEN** `cookie-plate.png` 得到 1 个圆，圆心与半径约为 `(264,258,244)`，误差不超过 10 px
