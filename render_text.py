#!  /usr/local/bin/python3

import sys
from skimage import io
from matplotlib import pyplot as plt

FILE_NAME = sys.argv[1]
TARGET_FILE = "textrender"

img = io.imread(FILE_NAME)

fig = plt.figure()
plt.imshow(img)
plt.text(400,400, "hello", color="white", fontsize=5)
fig.savefig(TARGET_FILE+".pdf", dpi=600, bbox_inches="tight")
