#!  /usr/local/bin/python3
# command SOURCE_TSV SOURCE_IMG_1 SOURCE_IMG_2 TARGET_FILE(.cor)

import sys
import numpy as np
from skimage import io, img_as_ubyte
from skimage.filters import threshold_otsu
from matplotlib import pyplot as plt

# parameters
SOURCE_TSV = sys.argv[1]
SOURCE_IMG_1 = sys.argv[2]
SOURCE_IMG_2 = sys.argv[3]
TARGET_FILE = sys.argv[4]+".cor"
FORE_ONLY = True

nuclei_list = []
with open(SOURCE_TSV, "r") as f:
	for i in f.readlines():
		nuclei_list.append(i[:-1].split("\t")[:-1])

usr_img_1 = img_as_ubyte(io.imread(SOURCE_IMG_1))
usr_img_2 = img_as_ubyte(io.imread(SOURCE_IMG_2))

brightness_cor = []
for i in nuclei_list:
	min_row = int(i[2])
	min_col = int(i[3])
	max_row = int(i[4])
	max_col = int(i[5])
	img_1_seg = usr_img_1[min_row:max_row, min_col:max_col]
	img_2_seg = usr_img_2[min_row:max_row, min_col:max_col]
	if FORE_ONLY == True:
		img_1_thresh = threshold_otsu(img_1_seg)
		img_1_binary = img_1_seg > img_1_thresh
		img_1_binary = img_1_binary.flatten()
		img_1_seg = img_1_seg.flatten()
		img_2_seg = img_2_seg.flatten()
		img_1_temp = np.array([])
		img_2_temp = np.array([])
		for j in range(img_1_seg.size):
			if img_1_binary[j] == True:
				img_1_temp = np.append(img_1_temp, img_1_seg[j])
				img_2_temp = np.append(img_2_temp, img_2_seg[j])
		img_1_seg = img_1_temp
		img_2_seg = img_2_temp
	else:
		img_1_seg = img_1_seg.flatten()
		img_2_seg = img_2_seg.flatten()
	brightness_cor.append(np.corrcoef(img_1_seg, img_2_seg)[0,1])

print("Corr median:{} min:{} max:{}".format(np.median(brightness_cor),\
	np.min(brightness_cor), np.max(brightness_cor)))
with open(TARGET_FILE, "w") as f:
	for i in brightness_cor:
		f.write("%s\n" % i)
