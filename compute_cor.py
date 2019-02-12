#!  /usr/local/bin/python3

import numpy as np
from skimage import io, img_as_ubyte
from matplotlib import pyplot as plt

# parameters
SOURCE_TSV = "./test.tsv"
SOURCE_IMG_1 = "./sample-img/CON-1-3_R3D_D3D_VOL_w525.tif"
SOURCE_IMG_2 = "./sample-img/CON-1-3_R3D_D3D_VOL_w676.tif"
TARGET_FILE = "./test_output"

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
print(brightness_cor)

# fig, ax = plt.subplots(nrows=1, ncols=2)
# ax[0].imshow(usr_img_1, cmap="gray")
# ax[0].set_title("img1")
# ax[1].imshow(usr_img_2, cmap="gray")
# ax[1].set_title("img2")
# fig.savefig(TARGET_FILE+".pdf", dpi=600, bbox_inches="tight")
