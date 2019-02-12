#!  /usr/local/bin/python3

# parameters
SOURCE_TSV = "./test.tsv"
SOURCE_IMG_1 = "./sample-img/CON-1-3_R3D_D3D_VOL_w525.tif"
SOURCE_IMG_2 = "./sample-img/CON-1-3_R3D_D3D_VOL_w676.tif"

nuclei_list = []
with open(SOURCE_TSV, "r") as f:
	for i in f.readlines():
		nuclei_list.append(i[:-1].split("\t")[:-1])
print(nuclei_list)

