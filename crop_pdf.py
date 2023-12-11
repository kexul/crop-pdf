import os
import sys
import shutil
import fitz
import shlex
import ghostscript
from PyQt5.QtWidgets import QApplication, QMenu, QFileDialog, QMainWindow, QAction
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

from mouse_drag import MyWidget

HOME_DIR = os.path.expanduser("~")


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.doc = None
        self.setWindowTitle('Crop PDF')
        self.mylabel = MyWidget()
        self.createActions()
        self.createMenuBar()
        self.mylabel.sig_mouse_released[int, int, int, int].connect(self.crop_all_pages)
        self.setCentralWidget(self.mylabel)
    

    def createActions(self):
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.openAction.triggered.connect(self.update_image)

        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(self.close)

        self.cropAction = QAction("&Crop", self)
        self.cropAction.triggered.connect(self.enable_selection)
        self.compressAction = QAction("&Compress", self)
        self.compressAction.triggered.connect(self.on_comp)

    def createMenuBar(self):
        menuBar = self.menuBar()

        fileMenu = QMenu("&File", self)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.exitAction)

        toolMenu = QMenu("&Tool", self)
        toolMenu.addAction(self.cropAction)
        toolMenu.addAction(self.compressAction)

        menuBar.addMenu(fileMenu)
        menuBar.addMenu(toolMenu)

    def update_image(self):
        fileName, _ = QFileDialog.getOpenFileName(self,"Open Pdf","","Pdf Files (*.pdf)")
        if fileName:
            self.doc = fitz.open(fileName)
            page = self.doc.load_page(3)

            pix = page.get_pixmap()
            # set the correct QImage format depending on alpha
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            qtimg = QImage(pix.samples_ptr, pix.width, pix.height, fmt)
            self.mylabel.setPixmap(QPixmap.fromImage(qtimg))
    
    def crop_all_pages(self, sx, sy, ex, ey):
        if ex - sx > 10 and ey - sy > 10:
            for number_of_page in range(self.doc.page_count):
                page = self.doc.load_page(number_of_page)
                page.set_mediabox(fitz.Rect(sx, sy, ex, ey))
            fileName, _ = QFileDialog.getSaveFileName(self,"Save to PDF", HOME_DIR, "Pdf Files (*.pdf)")
            if fileName:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.doc.save(fileName)
                self.destructive_crop(fileName)
                QApplication.restoreOverrideCursor()

    def on_comp(self):
        fileName, _ = QFileDialog.getSaveFileName(self,"Save to PDF",HOME_DIR,"Pdf Files (*.pdf)")
        if fileName:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.doc.save(fileName)
            self.compress_pdf_gh(fileName)
            QApplication.restoreOverrideCursor()
            
    # destructive crop pdf by ghost script: https://stackoverflow.com/questions/457207/cropping-pages-of-a-pdf-file#comment95568261_465901
    def destructive_crop(self, file_path):
        command = f'gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile={file_path}.pdf {file_path}'
        ghostscript.Ghostscript(*shlex.split(command))
        shutil.move(f'{file_path}.pdf', file_path)

    # compress by ghost script: https://gist.github.com/ahmed-musallam/27de7d7c5ac68ecbd1ed65b6b48416f9
    # -dCompatibilityLevel=1.4 should be used, 1.3 not working
    def compress_pdf_gh(self, file_path):
        command = f'gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dEmbedAllFonts=true -dSubsetFonts=true -dColorImageDownsampleType=/Bicubic -dColorImageResolution=144 -dGrayImageDownsampleType=/Bicubic -dGrayImageResolution=144 -dMonoImageDownsampleType=/Bicubic -dMonoImageResolution=144 -sOutputFile={file_path}.pdf {file_path}'
        ghostscript.Ghostscript(*shlex.split(command))
        shutil.move(f'{file_path}.pdf', file_path)
    
    def enable_selection(self):
        if self.doc is not None:
            self.mylabel.activate_selection = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())