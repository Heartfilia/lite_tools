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
from math import ceil
from typing import Union, Optional

try:
	from PIL import Image
	from reportlab.pdfgen import canvas
	from reportlab.lib.pagesizes import landscape
except ImportError:
	raise ImportError

from lite_tools.logs import logger


def _generate_pdf(filename: str, page_sizes: tuple = None) -> canvas.Canvas:
	"""
	开始绘制pdf了
	:param filename: 文件的名称啦
	:param page_sizes: 文件的分辨率 (宽, 高)  全局尺寸
	"""
	pdf = canvas.Canvas(filename)
	if page_sizes:
		pdf.setPageSize(page_sizes)
	return pdf


def _save_img_to_pdf(
		pdf: canvas.Canvas, image_path: str,
		x: Union[int, float], y: Union[int, float], w: Union[int, float], h: Union[int, float],
		set_size: bool = False) -> None:
	"""
	把图片绘制进pdf对象
	:param pdf       : 当然是pdf的canvas对象
	:param image_path: 单个图片的路径
	:param x         :
	:param y         :
	:param w         : 图片的宽像素
	:param h         : 图片的高像素
	:param set_size  : 图片的高像素
	"""
	if set_size is False:       # 没有设置全局尺寸的情况下
		pdf._pagesize = (w, h)  # 配置当前页的大小
	pdf.drawImage(image_path, x, y, w, h)
	pdf.showPage()


def lite_pdf(file_dir: str, out_name: str, width: int = -1, height: int = -1) -> None:
	"""
	主要的处理方式 -- 这里可以直接代码调用
	:param file_dir: 传入的文件路径
	:param out_name: 输出文件的名称
	:param width   : 输出文件的宽度
	:param height  : 输出文件的高度
	"""
	pdf_size = (width, height)
	if '.pdf' not in out_name:
		out_dir = f"{out_name}.pdf"
	else:
		out_dir = out_name

	if width != -1 and height != -1:  # 如果传入了 直接用这个大小
		my_pdf = _generate_pdf(out_dir, pdf_size)
		set_size = True
	else:   # 不传入的话 那么后面初始话 使用第一张图片的尺寸作为基准
		my_pdf = None
		set_size = False
	if not os.path.isdir(file_dir):
		file_list = [file_dir]
	else:
		file_list = os.listdir(file_dir)

	file_list.sort()   # 修复乱序问题
	len_file = len(file_list)

	first_pic = True
	temp_folder = []
	for ind, filename in enumerate(file_list):
		if not re.search(r"\.jpg$|\.jpeg$|\.png$", filename, re.I):
			continue
		if file_dir == filename:
			file_dir = os.getcwd()
		pic_root = os.path.join(file_dir, filename)
		img = Image.open(pic_root)
		img_w, img_h = img.size   # 原始图片的尺寸
		if first_pic and my_pdf is None:
			# my_pdf = _generate_pdf(out_dir, (img_w, img_h))
			my_pdf = _generate_pdf(out_dir)
			first_pic = False

		x = 0
		y = 0
		if not my_pdf:
			print("初始话pdf模板错误,可以尝试手动添加模板尺寸")
			exit(0)
		if set_size:  # 如果是设置了尺寸 需要做到适配尺寸
			if img_w > width or img_h > height:  # 如果两个边有一边比预设的大
				w_rate = round(width / img_w, 2)
				h_rate = round(height / img_h, 2)
				goal_rate = min(w_rate, h_rate)   # 哪个变化大取哪个
				new_w = ceil(img_w * goal_rate)
				new_h = ceil(img_h * goal_rate)
				# 先把宽度对齐，然后看看高度是否需要调整
				img = img.resize(size=(new_w, new_h))
				temp_name = os.path.join(file_dir, f"~temp_lite_image_{filename}")
				img.save(temp_name)
				temp_folder.append(temp_name)
				x = abs((width - new_w) // 2)
				y = abs((height - new_h) // 2)
				img_w = new_w
				img_h = new_h
				pic_root = temp_name
			else:
				x = abs((width - img_w) // 2)
				y = abs((height - img_h) // 2)

		img.close()
		_save_img_to_pdf(my_pdf, pic_root, x=x, y=y, w=img_w, h=img_h, set_size=set_size)
		print(f'\r[{ind+1:>03}/{len_file:>03}] image--{filename}--saved ', end="")
	my_pdf.save()
	print()
	logger.success("转换完成")
	for temp_name in temp_folder:
		os.remove(temp_name)


def _split_folder(folder: str) -> str:
	"""
	切割文件夹 取文件夹最后一个名称作为名字
	"""
	if "/" in folder:
		out_items = folder.split('/')
		for item in range(len(out_items)-1, -1, -1):
			out_name = out_items[item]
			if out_name and out_name not in ["."]:
				return out_name
	elif "\\" in folder:
		out_items = folder.split("\\")
		for item in range(len(out_items)-1, -1, -1):
			out_name = out_items[item]
			if out_name and out_name not in ["."]:
				return out_name
	else:
		return folder


def _check_legal(out_dir):
	# 这里需要检查一下输出的路径是否包含非法字符
	if out_dir and not out_dir.endswith('.pdf'):
		out_dir += ".pdf"
	elif out_dir and out_dir.endswith('.pdf'):
		pass
	else:
		logger.warning("检查输出的文件路径是否正确")
		sys.exit(0)
	# 判断字符是否合法
	if not re.search(r"[?:*\"<>|']+", out_dir) or re.search(r"^\w:\\", out_dir) or re.search(r"^\w:/", out_dir):
		return out_dir
	else:
		return None


def _has_out_name(cmd_cwd: str, out_name: str) -> Optional[str]:
	"""
	这里是拆分了下面功能 提取出来了有传入out_name的情况的时候的处理方式
	"""
	if out_name.endswith('.pdf'):
		out_dir = out_name
	elif os.path.isdir(out_name) or os.path.isdir(os.path.join(cmd_cwd, out_name)):
		out_dir = os.path.join(cmd_cwd, _split_folder(out_name))
	else:
		out_dir = os.path.join(cmd_cwd, re.sub(r"\.\w+", "", _split_folder(out_name)))

	return _check_legal(out_dir)


def _not_have_out_name(cmd_cwd, full_path) -> Optional[str]:
	out_dir = os.path.join(cmd_cwd, re.sub(r"\.\w+", "", _split_folder(full_path)))

	return _check_legal(out_dir)


def _judge_file_or_folder(location_name: str, out_name: str = None):
	"""
	判断传入的是文件还是文件夹
	"""
	cmd_cwd = os.getcwd()

	if os.path.exists(location_name) and not os.path.isfile(location_name):
		full_path = location_name
	elif os.path.exists(os.path.join(cmd_cwd, location_name)):
		full_path = os.path.join(cmd_cwd, location_name)
	else:
		logger.warning("需要传入准确的文件或者文件夹路径或者名称")
		sys.exit(0)

	if out_name:
		new_out_name = _has_out_name(cmd_cwd, out_name)
	else:
		new_out_name = _not_have_out_name(cmd_cwd, full_path)
	if not new_out_name:
		logger.warning("需要传入准确的文件或者文件夹路径或者名称")
		sys.exit(0)
	result = new_out_name if not re.search(r"^\.\S+", new_out_name) else f"lite_pdf_{new_out_name}"

	return result


# ------------------------- 命令行调用入口 ----------------------------


def _print_pdf_base():
	base_info = "lite_tools trans [-h] [-i ...] [-m ...] [-o ...] [-w ...] [-l ...]\n\n"
	base_info += "输出对应的文件信息 下面是 注意事项:\n"
	base_info += "1.同名文件会被覆盖 我这不会创建文件夹 会输出在已有文件夹\n"
	base_info += "2.如果输出的文件路径有空格则会出现问题，会默认输出到终端当前运行路径\n\n"
	base_info += "optional arguments:\n  "
	base_info += "-h, --help        show this help message and exit\n  "
	base_info += "-m, --mode        [ 处理模式 ] 默认处理pdf模式:如 -m pdf, -m word, -m pic, -m excel\n  "
	base_info += "-i, --input       必填参数-后跟需要处理的文件夹或者文件路径\n  "
	base_info += "-o, --output      [基于-i参数] 默认输出到当前位置,不填默认和处理文件夹或者文件同名\n  "
	base_info += "-w, --width       [基于-i参数] 输出文件的像素宽度-默认采用第一张图片的宽度\n  "
	base_info += "-h, --height      [基于-i参数] 输出文件的像素长度-默认采用第一张图片的高度"
	print(base_info)


def pdf_run(args):
	"""
	这里主要是给终端命令行调用的时候使用的
	"""
	if len(args) <= 2 or args[1] in ("-h", "--help"):
		_print_pdf_base()
		return
	args_string = " ".join(args)

	_input_string = re.search(r"-i\s+(\S+)", args_string) or re.search(r"--input\s+(\S+)", args_string)
	_output_string = re.search(r"-o\s+(\S+)", args_string) or re.search(r"--output\s+(\S+)", args_string)
	_width_string = re.search(r"-w\s+(\d+)", args_string) or re.search(r"--width\s+(\d+)", args_string)
	_height_string = re.search(r"-h\s+(\d+)", args_string) or re.search(r"--height\s+(\d+)", args_string)
	if _input_string:
		# 下面所有操作都是基于输入字符串存在的处理模式
		default_width = -1
		default_height = -1
		out_dir = None
		input_info = _input_string.group(1)

		if _output_string:
			out_dir = _output_string.group(1)
		output_info = _judge_file_or_folder(input_info, out_dir)

		if _width_string:
			width_info = _width_string.group(1)
			if width_info.isdigit():
				default_width = int(width_info)

		if _height_string:
			height_info = _height_string.group(1)
			if height_info.isdigit():
				default_height = int(height_info)

		# 注意文件要是输出的时候本地已经有同名的文件了得加后缀
		lite_pdf(input_info, output_info, default_width, default_height)

	else:
		_print_pdf_base()


if __name__ == '__main__':
	# lite_pdf(
	# 	r"/Users/lodge/TmpFiles/pics/xu",
	# 	"test.pdf",
	# 	1080,
	# 	1920
	# )

	_judge_file_or_folder("xu", None)
