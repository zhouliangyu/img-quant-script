#!  /usr/local/bin/python3
# command SOURCE_TSV SOURCE_IMG_1 SOURCE_IMG_2 TARGET_FILE(.cor)

import sys
import numpy as np
from skimage import io, img_as_ubyte
from matplotlib import pyplot as plt

# parameters
SOURCE_TSV = sys.argv[1]
SOURCE_IMG_1 = sys.argv[2]
SOURCE_IMG_2 = sys.argv[3]
TARGET_FILE = sys.argv[4]+".cor"

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
	img_1_seg = usr_img_1[min_row:max_row, min_col:max_col].flatten()
	img_2_seg = usr_img_2[min_row:max_row, min_col:max_col].flatten()
	brightness_cor.append(np.corrcoef(img_1_seg, img_2_seg)[0,1])

with open(TARGET_FILE, "w") as f:
	for i in brightness_cor:
		f.write("%s\n" % i)
