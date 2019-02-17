#!/usr/local/bin/python3
# ./command SOURCE_FILE CONFIG_FILE

import sys

from skimage import io, img_as_ubyte
from skimage.filters import threshold_otsu
from skimage.morphology import watershed, closing, square
from skimage.feature import peak_local_max
from skimage.measure import regionprops

from matplotlib import pyplot as plt
import numpy as np
from scipy.ndimage.morphology import binary_fill_holes
from scipy import ndimage as ndi

SOURCE_FILE = sys.argv[1]
CONFIG_FILE = sys.argv[2]
ori_usr_img = img_as_ubyte(io.imread(SOURCE_FILE))

# default parameters
params = {}
params['ROI_MIN_ROW'] = 0
params['ROI_MIN_COL'] = 0
params['ROI_MAX_ROW'] = ori_usr_img.shape[0] - 1
params['ROI_MAX_COL'] = ori_usr_img.shape[1] - 1
params['SHOW_IMG'] = 0
params['SAVE_FILE'] = 1
params['MIN_OBJ_AREA'] = 900 # a good pach nucleus is about 1500
params['MAX_OBJ_AREA'] = 2000
params['BBOX_RATIO_THRES'] = 0.5
params['NUM_ITER'] = 75
params['ITER_STEP'] = 0.4
params['TEXT_RENDER'] = 1
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

CLOSING_ORDER = np.arange(1, 999, params['ITER_STEP'])


usr_img = ori_usr_img[params['ROI_MIN_ROW']:params['ROI_MAX_ROW'], \
                  params['ROI_MIN_COL']:params['ROI_MAX_COL']]
thres_img = usr_img > threshold_otsu(usr_img)
filled_img = binary_fill_holes(thres_img)

iter_remaining = params['NUM_ITER']
num_of_nuclei = 0
temp_list = []
while iter_remaining > 0:
	watershed_mask = filled_img
	dist = ndi.distance_transform_edt(filled_img)
	footprint_min = np.ones((3,3)) # minimum footprint for finding local max, not helpful if too big - e.g. set to 10, even very easily found nuclei got missed
	local_max = peak_local_max(dist, indices=False, footprint=footprint_min,
		labels=filled_img)
	markers = ndi.label(local_max)[0]
	labels = watershed(-dist, markers, mask=watershed_mask)
	regions = regionprops(labels)
	temp_img = usr_img
	for i in regions:
		obj_area = i.area
		obj_bbox_area = i.bbox_area
		obj_cen_row, obj_cen_col = i.centroid
		obj_min_row, obj_min_col, obj_max_row, obj_max_col = i.bbox
		if obj_max_row > temp_img.shape[0]-1:
			obj_max_row = temp_img.shape[0]-1
		if obj_max_col > temp_img.shape[1]-1:
			obj_max_col = temp_img.shape[1]-1
		obj_bbox_ratio = (obj_max_row-obj_min_row)/(obj_max_col-obj_min_col)
		if obj_area < params['MIN_OBJ_AREA'] or \
		   obj_area > params['MAX_OBJ_AREA']: continue
		if obj_bbox_ratio < params['BBOX_RATIO_THRES'] or \
		   obj_bbox_ratio > 1/params['BBOX_RATIO_THRES']: continue
		print("No.{} in iteration {}/{}".format(num_of_nuclei,
			params['NUM_ITER']-iter_remaining+1, params['NUM_ITER']))

		temp_list.append([int(round(obj_cen_row))+params['ROI_MIN_ROW'], \
		                  int(round(obj_cen_col))+params['ROI_MIN_COL'], \
                          obj_min_row+params['ROI_MIN_ROW'], \
                          obj_min_col+params['ROI_MIN_COL'], \
                          obj_max_row+params['ROI_MIN_ROW'], \
                          obj_max_col+params['ROI_MIN_COL']])

		num_of_nuclei += 1

		ori_usr_img[obj_min_row+params['ROI_MIN_ROW']:obj_max_row+params['ROI_MIN_ROW'], obj_min_col+params['ROI_MIN_COL']] = 255
		ori_usr_img[obj_min_row+params['ROI_MIN_ROW']:obj_max_row+params['ROI_MIN_ROW'], obj_max_col+params['ROI_MIN_COL']] = 255
		ori_usr_img[obj_min_row+params['ROI_MIN_ROW'], obj_min_col+params['ROI_MIN_COL']:obj_max_col+params['ROI_MIN_COL']] = 255
		ori_usr_img[obj_max_row+params['ROI_MIN_ROW'], obj_min_col+params['ROI_MIN_COL']:obj_max_col+params['ROI_MIN_COL']] = 255

		filled_img[obj_min_row:obj_max_row, obj_min_col:obj_max_col] = 0
	filled_img = closing(filled_img, \
	square(int(round(CLOSING_ORDER[params['NUM_ITER'] - iter_remaining]))))
	filled_img = binary_fill_holes(filled_img)
	iter_remaining -= 1

fig = plt.figure()
plt.imshow(ori_usr_img)
if params['TEXT_RENDER']:
	for i in temp_list:
		plt.text(i[1],i[0], "r{}c{}".format(i[0],i[1]), color="white",\
		fontsize=3)
if params['SHOW_IMG']:
	plt.show()
elif params['SAVE_FILE']:
	fig.savefig(SOURCE_FILE+".pdf", dpi=600, bbox_inches="tight")
	with open(SOURCE_FILE+".tsv", "w") as f:
		for i in temp_list:
			for j in i:
				f.write("%s\t" % j)
			f.write("\n")


