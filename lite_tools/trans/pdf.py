# -*- coding: utf-8 -*-
# @Time   : 2021-04-08 14:23
# @Author : Lodge
"""
这里后面再拓展拉 包括但不限于下面的功能
这里涉及的功能都是转换pdf的 图片->pdf【第一版先做这个】  文字->pdf  表格->pdf  网页->pdf
"""
import os
import re
import sys
from typing import Union

try:
	import PIL
	from reportlab.pdfgen import canvas
	from reportlab.lib.pagesizes import landscape
except ImportError:
	raise ImportError

from lite_tools.utils_jar.logs import logger


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


def _judge_file_or_folder(location_name: str):
	"""
	判断传入的是文件还是文件夹
	"""
	if os.path.isdir(location_name):
		if "/" in location_name:
			out_name = location_name.split('/')[-1]
		elif "\\" in location_name:
			out_name = location_name.split("\\")[-1]
		else:
			out_name = "lite_tools_pdf"
		return True, out_name
	elif os.path.isfile(location_name):
		return False, "".join(location_name.split(".")[:-1])
	else:
		logger.warning("需要传入准确的文件或者文件夹路径或者名称")
		sys.exit(0)


# ------------------------- 命令行调用入口 ----------------------------


def _print_pdf_base():
	base_info = "lite_tools trans [-h] [-i ...] [-m ...] [-o ...] [-w ...] [-l ...]\n\n"
	base_info += "输出对应的文件信息\n\n"
	base_info += "optional arguments:\n  "
	base_info += "-h, --help        show this help message and exit\n  "
	base_info += "-m, --mode        [ 处理模式 ] 默认处理pdf模式:如 -m pdf, -m word, -m pic, -m excel\n  "
	base_info += "-i, --input       必填参数-后跟需要处理的文件夹或者文件路径\n  "
	base_info += "-o, --output      [基于-i参数] 默认输出到当前位置,不填默认和处理文件夹或者文件同名\n  "
	base_info += "-w, --width       [基于-i参数] 输出文件的像素宽度-默认1920\n  "
	base_info += "-l, --length      [基于-i参数] 输出文件的像素长度-默认1080"
	print(base_info)


def pdf_run(args):
	if len(args) <= 2 or args[1] in ("-h", "--help"):
		_print_pdf_base()
		return
	args_string = " ".join(args)

	_input_string = re.search(r"-i\s+(\S+)", args_string) or re.search(r"--input\s+(\S+)", args_string)
	_output_string = re.search(r"-o\s+(\S+)", args_string) or re.search(r"--output\s+(\S+)", args_string)
	_width_string = re.search(r"-w\s+(\d+)", args_string) or re.search(r"--width\s+(\d+)", args_string)
	_length_string = re.search(r"-l\s+(\d+)", args_string) or re.search(r"--length\s+(\d+)", args_string)
	if _input_string:
		# 下面所有操作都是基于输入字符串存在的处理模式
		default_width = 1080
		default_length = 1920
		input_info = _input_string.group(1)
		is_dir, output_info = _judge_file_or_folder(input_info)

		if _output_string:
			output_info = _output_string.group(1)

		if _width_string:
			width_info = _width_string.group(1)
			if width_info.isdigit():
				default_width = int(width_info)

		if _length_string:
			length_info = _length_string.group(1)
			if length_info.isdigit():
				default_length = int(length_info)

		# 注意文件要是输出的时候本地已经有同名的文件了得加后缀
		print(input_info, is_dir, output_info, default_width, default_length)

	else:
		_print_pdf_base()


if __name__ == "__main__":
	# pdf_run(["o.py", "-i", "xxx", "--output", "yyy"])
	pdf_run(["o.py", "-m", "pdf", "-i", "excel.py", "--output", "yyy", "-w", "16666", "-l", "99999"])
	pdf_run(["o.py", "-m", "pdf", "-i", "excel.py", "-w", "16666", "-l", "99999"])
	pdf_run(["o.py", "-m", "pdf", "-i", "../trans", "--output", "yyy"])
	pdf_run(["o.py", "-m", "pdf", "-i", "../trans"])
	pdf_run(["o.py", "-m", "pdf", "-i", "sdfsdfsd"])
