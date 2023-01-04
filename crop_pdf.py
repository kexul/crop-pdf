import sys
import fitz
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QImage, QPixmap

from mouse_drag import MyWidget


class LaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.update_image()
    
    def update_image(self):
        fileName, _ = QFileDialog.getOpenFileName(self,"Open Pdf","","Pdf Files (*.pdf)")
        if fileName:
            self.doc = fitz.open(fileName)
            page = self.doc.load_page(10)

            pix = page.get_pixmap()
            # set the correct QImage format depending on alpha
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            qtimg = QImage(pix.samples_ptr, pix.width, pix.height, fmt)
            self.mylabel.setPixmap(QPixmap.fromImage(qtimg))


    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.mylabel = MyWidget()
        layout.addWidget(self.mylabel)

        self.mylabel.sig_mouse_released[int, int, int, int].connect(self.crop_all_pages)
    
    def crop_all_pages(self, sx, sy, ex, ey):
        if ex - sx > 10 and ey - sy > 10:
            for number_of_page in range(self.doc.page_count):
                page = self.doc.load_page(number_of_page)
                page.set_cropbox(fitz.Rect(sx, sy, ex, ey))
            fileName, _ = QFileDialog.getSaveFileName(self,"Save to Pdf","","Pdf Files (*.pdf)")
            if fileName:
                self.doc.save(fileName)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = LaWidget()
    w.show()
    sys.exit(app.exec_())