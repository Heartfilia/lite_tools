# -*- coding: utf-8 -*-
# @Time   : 2021-04-08 14:23
# @Author : Lodge
"""
这里后面再拓展拉 包括但不限于下面的功能
"""
import os
import sys
from typing import Union

from lite_tools.utils_jar.logs import logger
try:
	import PIL
	from reportlab.pdfgen import canvas
	from reportlab.lib.pagesizes import landscape
except ImportError:
	logger.warning("需要安装 文件处理版-> lite-tools[file] 或者 完整版-> lite-tools[all] 功能方可体验")
	sys.exit(0)

# ------------------------ 表格功能块 ---------------------------


def csv2excel():
	pass


# ------------------------ 文字功能块 ----------------------------


def word2pdf():
	pass


# ------------------------- 图片功能块 ----------------------------


def img2pdf():
	pass


def _generate_pdf(filename: str, page_sizes: tuple) -> canvas.Canvas:
	"""
	开始绘制pdf了
	:param filename: 文件的名称啦
	:param page_sizes: 文件的分辨率 (宽, 高)
	"""
	pdf = canvas.Canvas(filename)
	pdf.setPageSize(page_sizes)
	return pdf


def _save_img_to_pdf(
		pdf: canvas.Canvas, image_path: str,
		x: Union[int, float], y: Union[int, float], w: Union[int, float], h: Union[int, float]) -> None:
	"""
	把图片绘制进pdf对象
	:param pdf       : 当然是pdf的canvas对象
	:param image_path: 单个图片的路径
	:param x         :
	:param y         :
	:param w         : 图片的宽像素
	:param h         : 图片的高像素
	"""
	pdf.drawImage(image_path, x, y, w, h)
	pdf.showPage()
