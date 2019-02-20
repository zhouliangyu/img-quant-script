#!  /usr/local/bin/python3

from skimage import io
from skimage.feature import blob_log
from skimage import img_as_ubyte
from matplotlib import pyplot as plt

img = img_as_ubyte(io.imread("samples/mut-1-3-525.tif"))
img = img[350:400,250:300]
labeled = img
blobs_log = blob_log(img, min_sigma=0.4, max_sigma=50, num_sigma=20, threshold=0.05, overlap=0.5)
print(blobs_log)
print("length:{}".format(len(blobs_log)))

fig, ax = plt.subplots(nrows=1, ncols=2)
ax[0].imshow(img)
ax[1].imshow(labeled)
for i in blobs_log:
	ax[1].text(round(i[1]), round(i[0]), "*", fontsize=15, color="red")

plt.savefig("test.pdf")
