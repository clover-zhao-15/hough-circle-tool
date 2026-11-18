"""Main window: import, tune, preview and export annotated images."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSpinBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .detector import Circle, annotate, detect_circles
from .params import HoughParams

IMAGE_FILTER = "图片 (*.jpg *.jpeg *.png *.bmp)"


@dataclass
class ImageEntry:
    path: Path
    image: np.ndarray
    circles: list[Circle]
    annotated: np.ndarray
    elapsed_ms: float


def _to_pixmap(image: np.ndarray) -> QPixmap:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = rgb.shape[:2]
    qimage = QImage(
        rgb.data, width, height, rgb.strides[0], QImage.Format.Format_RGB888
    ).copy()
    return QPixmap.fromImage(qimage)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("霍夫圆检测工具")
        self.resize(1180, 760)
        self._entries: dict[Path, ImageEntry] = {}
        self._current: Path | None = None
        self._current_pixmap: QPixmap | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        toolbar = QToolBar("操作")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction("打开图片", self.open_images)
        toolbar.addAction("重新检测", self.redetect_all)
        toolbar.addAction("导出标注图", self.export_current)
        toolbar.addAction("重置参数", self.reset_params)

        self.dp_spin = QDoubleSpinBox()
        self.dp_spin.setRange(0.1, 4.0)
        self.dp_spin.setSingleStep(0.1)
        self.dp_spin.setDecimals(1)

        self.min_dist_spin = QSpinBox()
        self.min_dist_spin.setRange(1, 2000)
        self.min_dist_spin.setSuffix(" px")

        self.param1_spin = QSpinBox()
        self.param1_spin.setRange(1, 500)

        self.param2_spin = QSpinBox()
        self.param2_spin.setRange(1, 200)

        self.min_radius_spin = QSpinBox()
        self.min_radius_spin.setRange(0, 1000)
        self.min_radius_spin.setSuffix(" px")

        self.max_radius_spin = QSpinBox()
        self.max_radius_spin.setRange(0, 1000)
        self.max_radius_spin.setSuffix(" px")

        self._reset_widgets(HoughParams())

        form = QFormLayout()
        form.addRow("dp", self.dp_spin)
        form.addRow("minDist", self.min_dist_spin)
        form.addRow("param1", self.param1_spin)
        form.addRow("param2", self.param2_spin)
        form.addRow("minRadius", self.min_radius_spin)
        form.addRow("maxRadius", self.max_radius_spin)

        hint = QLabel("修改参数后点「重新检测」")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666;")

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addLayout(form)
        left_layout.addWidget(hint)
        left_layout.addStretch(1)

        self.file_list = QListWidget()
        self.file_list.setMinimumWidth(220)
        self.file_list.currentItemChanged.connect(self._on_file_selected)

        self.preview = QLabel("打开图片开始检测")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(480, 360)
        self.preview.setStyleSheet("background: #202020; color: #dddddd;")
        self.preview.installEventFilter(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.file_list)
        splitter.addWidget(self.preview)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 0)
        splitter.setStretchFactor(2, 1)
        splitter.setSizes([240, 240, 700])
        self.setCentralWidget(splitter)
        self.statusBar().showMessage("未加载图片")

    def _reset_widgets(self, params: HoughParams) -> None:
        self.dp_spin.setValue(params.dp)
        self.min_dist_spin.setValue(params.min_dist)
        self.param1_spin.setValue(params.param1)
        self.param2_spin.setValue(params.param2)
        self.min_radius_spin.setValue(params.min_radius)
        self.max_radius_spin.setValue(params.max_radius)

    def current_params(self) -> HoughParams:
        return HoughParams(
            dp=self.dp_spin.value(),
            min_dist=self.min_dist_spin.value(),
            param1=self.param1_spin.value(),
            param2=self.param2_spin.value(),
            min_radius=self.min_radius_spin.value(),
            max_radius=self.max_radius_spin.value(),
        )

    def open_images(self) -> None:
        start = Path.cwd() / "examples"
        if not start.is_dir():
            start = Path.home()
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", str(start), IMAGE_FILTER
        )
        if files:
            self.load_paths([Path(name) for name in files])

    def load_paths(self, paths: list[Path]) -> list[Path]:
        """Load and detect the given paths; returns paths actually added."""
        try:
            params = self.current_params()
            params.validate()
        except ValueError as exc:
            self.statusBar().showMessage(f"参数错误: {exc}", 8000)
            return []

        failures: list[str] = []
        added: list[Path] = []
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            for raw_path in paths:
                path = Path(raw_path).expanduser().resolve()
                if path in self._entries:
                    continue
                image = cv2.imread(str(path))
                if image is None:
                    failures.append(path.name)
                    continue
                try:
                    entry = self._detect(path, image, params)
                except (ValueError, cv2.error) as exc:
                    failures.append(f"{path.name}: {exc}")
                    continue
                self._entries[path] = entry
                item = QListWidgetItem(f"{path.name}  ({len(entry.circles)})")
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.file_list.addItem(item)
                added.append(path)
        finally:
            QApplication.restoreOverrideCursor()

        if failures:
            self.statusBar().showMessage("无法读取: " + ", ".join(failures), 8000)
        if added:
            self._select_path(added[0])
        return added

    def _detect(
        self, path: Path, image: np.ndarray, params: HoughParams
    ) -> ImageEntry:
        start = time.perf_counter()
        circles = detect_circles(image, params)
        annotated = annotate(image, circles)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ImageEntry(path, image, circles, annotated, elapsed_ms)

    def redetect_all(self) -> None:
        if not self._entries:
            self.statusBar().showMessage("请先打开图片", 4000)
            return
        params = self.current_params()
        try:
            params.validate()
        except ValueError as exc:
            QMessageBox.warning(self, "参数错误", str(exc))
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            for index in range(self.file_list.count()):
                item = self.file_list.item(index)
                path = Path(item.data(Qt.ItemDataRole.UserRole))
                entry = self._entries[path]
                updated = self._detect(path, entry.image, params)
                self._entries[path] = updated
                item.setText(f"{path.name}  ({len(updated.circles)})")
        finally:
            QApplication.restoreOverrideCursor()

        if self._current is not None:
            self._show_entry(self._entries[self._current])
        self.statusBar().showMessage(f"已重新检测 {len(self._entries)} 张图片", 5000)

    def _select_path(self, path: Path) -> None:
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if Path(item.data(Qt.ItemDataRole.UserRole)) == path:
                self.file_list.setCurrentItem(item)
                return

    def _on_file_selected(
        self, current: QListWidgetItem | None, previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            return
        path = Path(current.data(Qt.ItemDataRole.UserRole))
        entry = self._entries.get(path)
        if entry is None:
            return
        self._current = path
        self._show_entry(entry)

    def _show_entry(self, entry: ImageEntry) -> None:
        self._current_pixmap = _to_pixmap(entry.annotated)
        self._update_preview()
        self.statusBar().showMessage(
            f"{entry.path.name} | {len(entry.circles)} 个圆 | {entry.elapsed_ms:.1f} ms"
        )

    def _update_preview(self) -> None:
        if self._current_pixmap is None:
            return
        area = self.preview.size()
        if area.width() < 16 or area.height() < 16:
            return
        self.preview.setPixmap(
            self._current_pixmap.scaled(
                area,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        if watched is self.preview and event.type() == QEvent.Type.Resize:
            self._update_preview()
        return super().eventFilter(watched, event)

    def export_current(self) -> None:
        if self._current is None:
            self.statusBar().showMessage("请先选择一张图片", 4000)
            return
        default = self._current.with_name(f"{self._current.stem}_annotated.png")
        name, _ = QFileDialog.getSaveFileName(
            self, "导出标注图", str(default), "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if name:
            self.export_current_to(Path(name))

    def export_current_to(self, target: str | Path) -> bool:
        if self._current is None:
            return False
        path = Path(target)
        if not path.suffix:
            path = path.with_suffix(".png")
        entry = self._entries[self._current]
        extension = path.suffix.lower()
        if extension not in {".png", ".jpg", ".jpeg"}:
            QMessageBox.warning(self, "导出失败", "仅支持 PNG、JPG、JPEG 扩展名")
            return False
        ok, buffer = cv2.imencode(extension, entry.annotated)
        if not ok:
            QMessageBox.warning(self, "导出失败", "图片编码失败")
            return False
        path.write_bytes(buffer.tobytes())
        self.statusBar().showMessage(f"已导出: {path}", 6000)
        return True

    def reset_params(self) -> None:
        self._reset_widgets(HoughParams())
        self.statusBar().showMessage("参数已重置", 4000)
