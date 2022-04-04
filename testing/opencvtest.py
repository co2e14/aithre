from PyQt5 import QtCore, QtWidgets


class Text(QtWidgets.QTextEdit):
    mousePressSignal = QtCore.pyqtSignal(str)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            text = "test: {}-{}".format(event.pos().x(), event.pos().y())
            self.mousePressSignal.emit(text)


class OtherWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OtherWidget, self).__init__(parent)
        self.label = QtWidgets.QLabel()
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)

    @QtCore.pyqtSlot(str)
    def setText(self, text):
        self.label.setText(text)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    t = Text()
    o = OtherWidget()
    o.resize(640, 480)
    t.mousePressSignal.connect(o.setText)
    t.show()
    o.show()
    sys.exit(app.exec_())
