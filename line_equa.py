#!  /usr/local/bin/python3
# (x1,y1),(x2,y2) -> y=ax+b
# command x1 y1 x2 y2 usr_x usr_y


import sys

if len(sys.argv) < 7:
	print("command x1 y1 x2 y2 usr_x usr_y")
	sys.exit()

x1 = int(sys.argv[1])
y1 = int(sys.argv[2])
x2 = int(sys.argv[3])
y2 = int(sys.argv[4])
usr_x = int(sys.argv[5])
usr_y = int(sys.argv[6])

slope = (y2-y1)/(x2-x1)
intercept = slope*(-x1)+y1

print("y = ax + b, a = {}, b = {}". format(slope,intercept))

theo_y = usr_x * slope + intercept

if theo_y >= usr_y:
	print("One side")
else:
	print("The ohter side")


