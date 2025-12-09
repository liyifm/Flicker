from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QByteArray, QBuffer, QIODevice


class ImageUtils:
    @staticmethod
    def pixmapToBase64(pixmap: QPixmap, fmt: str = "png", quality: int = -1) -> str:
        """返回类似 'data:image/png;base64,AAA...' 的字符串"""

        img: QImage = pixmap.toImage()
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buf, format=fmt, quality=quality)  # type: ignore
        buf.close()
        # 3) Base64 编码（bytes -> str）
        return "data:image/{};base64,{}".format(fmt.lower(), ba.toBase64().data().decode())  # type: ignore

    @staticmethod
    def base64ToPixmap(base64_str: str) -> QPixmap:
        """从类似 'data:image/png;base64,AAA...' 的字符串中解析出 QPixmap"""
        header, encoded = base64_str.split(',', 1)
        img_data = QByteArray.fromBase64(encoded.encode())  # type: ignore
        img = QImage()
        img.loadFromData(img_data)
        return QPixmap.fromImage(img)
