import os
import sys
import shutil
import fitz
import shlex
import ghostscript
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QShortcut
from PyQt5.QtGui import QImage, QPixmap, QKeySequence

from mouse_drag import MyWidget

HOME_DIR = os.path.expanduser("~")

# destructive crop pdf by ghost script: https://stackoverflow.com/questions/457207/cropping-pages-of-a-pdf-file#comment95568261_465901
def destructive_crop(file_path):
    command = f'gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile={file_path}.pdf {file_path}'
    ghostscript.Ghostscript(*shlex.split(command))
    shutil.move(f'{file_path}.pdf', file_path)

# compress by ghost script: https://gist.github.com/ahmed-musallam/27de7d7c5ac68ecbd1ed65b6b48416f9
# -dCompatibilityLevel=1.4 should be used, 1.3 not working
def compress_pdf_gh(file_path):
    command = f'gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dEmbedAllFonts=true -dSubsetFonts=true -dColorImageDownsampleType=/Bicubic -dColorImageResolution=144 -dGrayImageDownsampleType=/Bicubic -dGrayImageResolution=144 -dMonoImageDownsampleType=/Bicubic -dMonoImageResolution=144 -sOutputFile={file_path}.pdf {file_path}'
    ghostscript.Ghostscript(*shlex.split(command))
    shutil.move(f'{file_path}.pdf', file_path)

class LaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.update_image()
        self.shortcut_comp = QShortcut(QKeySequence('Ctrl+P'), self)
        self.shortcut_comp.activated.connect(self.on_comp)
    
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
                page.set_mediabox(fitz.Rect(sx, sy, ex, ey))
            fileName, _ = QFileDialog.getSaveFileName(self,"Save to Pdf", HOME_DIR, "Pdf Files (*.pdf)")
            if fileName:
                self.doc.save(fileName)
                destructive_crop(fileName)

    def on_comp(self):
        fileName, _ = QFileDialog.getSaveFileName(self,"Save to Pdf",HOME_DIR,"Pdf Files (*.pdf)")
        if fileName:
            self.doc.save(fileName)
            compress_pdf_gh(fileName)
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = LaWidget()
    w.show()
    sys.exit(app.exec_())