# Copied from: https://www.pythonguis.com/faq/use-mouse-drag-to-change-the-width-of-a-rectangle/

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


FREE_STATE = 1
BUILDING_SQUARE = 2
BEGIN_SIDE_EDIT = 3
END_SIDE_EDIT = 4


CURSOR_ON_BEGIN_SIDE = 1
CURSOR_ON_END_SIDE = 2


class MyWidget(QLabel):
    sig_mouse_released = pyqtSignal(int, int, int, int)
    def __init__(self):
        super().__init__()
        self.begin = QPoint()
        self.end = QPoint()

        self.state = FREE_STATE

        self.setMouseTracking(True)
        self.free_cursor_on_side = 0
        self.activate_selection = False
    

    def paintEvent(self, event):
        super().paintEvent(event)

        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

        if not self.free_cursor_on_side:
            return

        qp.setPen(QPen(Qt.black, 5, Qt.DashLine))
        if self.free_cursor_on_side == CURSOR_ON_BEGIN_SIDE:
            end = QPoint(self.end)
            end.setX(self.begin.x())
            qp.drawLine(self.begin, end)

        elif self.free_cursor_on_side == CURSOR_ON_END_SIDE:
            begin = QPoint(self.begin)
            begin.setX(self.end.x())
            qp.drawLine(self.end, begin)

    def cursor_on_side(self, e_pos) -> int:
        if not self.begin.isNull() and not self.end.isNull():
            y1, y2 = sorted([self.begin.y(), self.end.y()])
            if y1 <= e_pos.y() <= y2:

                # 5 resolution, more easy to pick than 1px
                if abs(self.begin.x() - e_pos.x()) <= 5:
                    return CURSOR_ON_BEGIN_SIDE
                elif abs(self.end.x() - e_pos.x()) <= 5:
                    return CURSOR_ON_END_SIDE

        return 0

    def mousePressEvent(self, event):
        if not self.activate_selection:
            return
        side = self.cursor_on_side(event.pos())
        if side == CURSOR_ON_BEGIN_SIDE:
            self.state = BEGIN_SIDE_EDIT
        elif side == CURSOR_ON_END_SIDE:
            self.state = END_SIDE_EDIT
        else:
            self.state = BUILDING_SQUARE

            self.begin = event.pos()
            self.end = event.pos()
            self.update()

    def applye_event(self, event):

        if self.state == BUILDING_SQUARE:
            self.end = event.pos()
        elif self.state == BEGIN_SIDE_EDIT:
            self.begin.setX(event.x())
        elif self.state == END_SIDE_EDIT:
            self.end.setX(event.x())

    def mouseMoveEvent(self, event):
        if self.state == FREE_STATE:
            self.free_cursor_on_side = self.cursor_on_side(event.pos())
            if self.free_cursor_on_side:
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.unsetCursor()
            self.update()
        else:
            self.applye_event(event)
            self.update()

    def mouseReleaseEvent(self, event):
        self.applye_event(event)
        self.state = FREE_STATE
        self.sig_mouse_released.emit(self.begin.x(), self.begin.y(), self.end.x(), self.end.y())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())