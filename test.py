#!/usr/local/bin/python3

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

# parameters
SHOW_IMG = False
SAVE_FILE = True
MIN_OBJ_AREA = 900 # a good pach nucleus is about 1500
MAX_OBJ_AREA = 2000
BBOX_RATIO_THRES = 0.5
NUM_ITER = 75
ITER_STEP = 0.4
CLOSING_ORDER = np.arange(1, 999, ITER_STEP)

SOURCE_FILE = sys.argv[1]
TARGET_FILE = sys.argv[2]

test_img = img_as_ubyte(io.imread(SOURCE_FILE))
thres_img = test_img > threshold_otsu(test_img)
filled_img = binary_fill_holes(thres_img)

iter_remaining = NUM_ITER
num_of_nuclei = 0
while iter_remaining > 0:
	watershed_mask = filled_img # TRUE values will be used for watershed
	dist = ndi.distance_transform_edt(filled_img)
	footprint_min = np.ones((3,3)) # minimum footprint for finding local max, not helpful if too big - e.g. set to 10, even very easily found nuclei got missed
	local_max = peak_local_max(dist, indices=False, footprint=footprint_min,
		labels=filled_img)
	markers = ndi.label(local_max)[0]
	labels = watershed(-dist, markers, mask=watershed_mask)

	regions = regionprops(labels)
	temp_list = []
	temp_img = test_img
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
		if obj_area < MIN_OBJ_AREA or obj_area > MAX_OBJ_AREA:
			continue
		if obj_bbox_ratio < BBOX_RATIO_THRES or \
			obj_bbox_ratio > 1/BBOX_RATIO_THRES:
			continue
		print("No.{} in interation {}/{}".format(num_of_nuclei,
			NUM_ITER-iter_remaining+1, NUM_ITER))
		num_of_nuclei += 1
		temp_img[obj_min_row:obj_max_row, obj_min_col] = 255
		temp_img[obj_min_row:obj_max_row, obj_max_col] = 255
		temp_img[obj_min_row, obj_min_col:obj_max_col] = 255
		temp_img[obj_max_row, obj_min_col:obj_max_col] = 255
		filled_img[obj_min_row:obj_max_row, obj_min_col:obj_max_col] = 0
	filled_img = closing(filled_img, square(int(round(CLOSING_ORDER[NUM_ITER - \
		iter_remaining]))))
	filled_img = binary_fill_holes(filled_img)
	iter_remaining -= 1

fig, ax = plt.subplots(nrows=1, ncols=2)
ax[0].imshow(filled_img, cmap="gray")
ax[0].set_title("filled")
ax[1].imshow(temp_img)
ax[1].set_title("selected")
if SHOW_IMG == True:
	fig.show()
elif SAVE_FILE == True:
	fig.savefig(TARGET_FILE, dpi=600, bbox_inches="tight")


