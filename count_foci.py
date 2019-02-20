#!  /usr/local/bin/python3
# command NUCLEI_COOR_FILE REGION_FILE FOCI_FILE CONFIG_FILE

import sys
import random
from skimage import io, img_as_ubyte
from skimage.filters import rank
from skimage.morphology import disk, binary_dilation, convex_hull_image
from skimage.feature import blob_log
from matplotlib import pyplot as plt
from scipy.ndimage.morphology import binary_fill_holes


if len(sys.argv) <5:
	print("command NUCLEI_COOR_FILE REGION_FILE FOCI_FILE CONFIG_FILE")
	sys.exit()

NUCLEI_COOR_FILE = sys.argv[1]
REGION_FILE = sys.argv[2]
FOCI_FILE = sys.argv[3]
CONFIG_FILE = sys.argv[4]
# default params
params = {}
params['OTSU_FAC'] = 5
params['DILATION_FAC'] = 2
params['MIN_SIGMA'] = 0.4
params['MAX_SIGMA'] = 50
params['NUM_SIGMA'] = 20
params['BACK_THRES'] = 0.05
params['OVERLAP_RATIO'] = 0.5
params['FOCI_GRAPH'] = 1
params['NUM_GRAPH_PAIR'] = 3
params['FONT_SIZE'] = 8
# load config file
with open(CONFIG_FILE, "r") as f:
	usr_params = f.read().splitlines()
for i in usr_params:
	if i[0] != "#":
		usr_params = i.split(":")
		try:
			params[usr_params[0]] = int(usr_params[1])
		except ValueError:
			params[usr_params[0]] = float(usr_params[1])

region_img = img_as_ubyte(io.imread(REGION_FILE))
otsu_thres = rank.otsu(region_img, disk(params['OTSU_FAC']))
binary_img = region_img >= otsu_thres
foci_img = img_as_ubyte(io.imread(FOCI_FILE))

# load nuclei coordinates
# cen_row, cen_col, min_row, min_col, max_row, max_col, X
nuclei_list = []
with open(NUCLEI_COOR_FILE, "r") as f:
	for i in f.readlines():
		nuclei_list.append(i[:-1].split("\t")[:-1])


foci_list = []
for i in nuclei_list:
	roi_region = region_img[int(i[2]):int(i[4]), int(i[3]):int(i[5])]
	roi_binary = binary_img[int(i[2]):int(i[4]), int(i[3]):int(i[5])]
	roi_foci = foci_img[int(i[2]):int(i[4]), int(i[3]):int(i[5])]
	roi_binary = binary_dilation(roi_binary, disk(params['DILATION_FAC']))
	roi_binary = binary_fill_holes(roi_binary)
	binary_img[int(i[2]):int(i[4]), int(i[3]):int(i[5])] = roi_binary
	foci = blob_log(roi_foci, min_sigma=params['MIN_SIGMA'], \
		max_sigma=params['MAX_SIGMA'], num_sigma=params['NUM_SIGMA'],\
		threshold=params['BACK_THRES'], overlap=params['OVERLAP_RATIO'])
	# X, cen_row, cen_col, foci_num, foci_list, off_list
	on_list = []
	off_list = []
	for j in foci:
		focus_row = int(j[0])
		focus_col = int(j[1])
		if focus_row < roi_binary.shape[0] and \
		   focus_col < roi_binary.shape[1] and \
		   roi_binary[focus_row,focus_col]:
			on_list.append(j)
		else:
			off_list.append(j)
			if focus_row >= roi_binary.shape[0]:
				print("X={}, focus_row={} >= binary.shape[0]={}".format(int(i[6]), focus_row, roi_binary.shape[0]))
			elif focus_col >= roi_binary.shape[1]:
				print("X={}, focus_col={} >= binary.shape[1]={}".format(int(i[6]), focus_col, roi_binary.shape[1]))
			elif not roi_binary[focus_row, focus_col]:
				print("X={}, roi_binary[{},{}]={}".format(int(i[6]),focus_row,focus_col, roi_binary[focus_row, focus_col]))
	foci_list.append([int(i[6]),int(i[0]),int(i[1]),len(on_list), \
					  on_list,off_list])

# console log the foci_list
for i in foci_list:
	print(i[:-2])

if params['FOCI_GRAPH']:
	random_list = []
	for i in range(params['NUM_GRAPH_PAIR']):
		random_list.append(random.randint(0, len(foci_list)))
	fig, ax = plt.subplots(nrows=params['NUM_GRAPH_PAIR'], ncols=3)
	for i in range(params['NUM_GRAPH_PAIR']):
		pos=random_list[i]
		pos_x = foci_list[pos][0]
		pos_blobs_num = foci_list[pos][3]
		pos_blobs_list = foci_list[pos][4]
		pos_blobs_off = foci_list[pos][5]
		pos_blobs_off_num = len(pos_blobs_off)
		nucl_min_row = int(nuclei_list[pos_x-1][2])
		nucl_min_col = int(nuclei_list[pos_x-1][3])
		nucl_max_row = int(nuclei_list[pos_x-1][4])
		nucl_max_col = int(nuclei_list[pos_x-1][5])
		ax[i][0].imshow(region_img[nucl_min_row:nucl_max_row, \
								   nucl_min_col:nucl_max_col])
		ax[i][1].imshow(binary_img[nucl_min_row:nucl_max_row, \
								   nucl_min_col:nucl_max_col])
		ax[i][2].imshow(foci_img[nucl_min_row:nucl_max_row, \
							     nucl_min_col:nucl_max_col])
		for j in pos_blobs_list:
			ax[i][0].text(round(j[1]), round(j[0]), "*", \
				fontsize=params['FONT_SIZE'], color="red")
			ax[i][1].text(round(j[1]), round(j[0]), "*", \
				fontsize=params['FONT_SIZE'], color="red")
			ax[i][2].text(round(j[1]), round(j[0]), "*", \
				fontsize=params['FONT_SIZE'], color="red")
		for j in pos_blobs_off:
			ax[i][0].text(round(j[1]), round(j[0]), "*", \
				fontsize=params['FONT_SIZE'], color="lightblue")
			ax[i][1].text(round(j[1]), round(j[0]), "*", \
				fontsize=params['FONT_SIZE'], color="lightblue")
			ax[i][2].text(round(j[1]), round(j[0]), "*", \
				fontsize=params['FONT_SIZE'], color="lightblue")
		ax[i][0].set_title("X={}".format(pos_x))
		ax[i][2].set_title("Total {}({})".format(pos_blobs_num, \
									             pos_blobs_off_num))
	plt.savefig("foci_diag.pdf")


