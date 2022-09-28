# import the necessary packages
import argparse
import cv2
import json
from select_points_array import *

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
image = None

# def click_and_crop(event, x, y, flags, param):
# 	# grab references to the global variables
# 	global refPt, cropping
# 	# if the left mouse button was clicked, record the starting
# 	# (x, y) coordinates and indicate that cropping is being
# 	# performed
# 	if event == cv2.EVENT_LBUTTONDOWN:
# 		refPt = [(x, y)]
# 		cropping = True
# 	# check to see if the left mouse button was released
# 	elif event == cv2.EVENT_LBUTTONUP:
# 		# record the ending (x, y) coordinates and indicate that
# 		# the cropping operation is finished
# 		refPt.append((x, y))
# 		cropping = False
# 		# draw a rectangle around the region of interest
# 		cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
# 		cv2.imshow("image", image)


def draw_points(image, points_lists):
	i = 0
	for points in points_lists:
		for point in points:
			cv2.rectangle(image, point, point, (0, 255, 0), 3)
			i += 1
	print ("Drawn {} points".format(i))


def group_colors(image, roi_pts, threshold = 20):
	color_lists = []
	for points in roi_pts:
		colors = []
		for point in points:
			B = int(image[point[1], point[0]][0])
			G = int(image[point[1], point[0]][1])
			R = int(image[point[1], point[0]][2])
			colors.append([R,G,B])
		color_lists.append(colors)
	print(color_lists)

	def color_diff_sq(a,b):
		sum = 0
		for p, q in zip(a,b):
			sum += (int(p)-int(q)) ** 2
		return sum

	uniq_colors = []
	group_lists = []
	for color_list in color_lists:
		group_list = []
		for color in color_list:
			index = -1
			for i, uinq in enumerate(uniq_colors):
				if color_diff_sq(uinq,color) < threshold:
					index = i
					break
			# Color Not Found
			if index == -1:
				uniq_colors.append(color)
				index = len(uniq_colors)-1

			# Save Index
			group_list.append(index)
			print(color, index)
		group_lists.append(group_list)

	print ("Analyzed {} Lists, {} Unique Colors".format(len(color_lists), len(uniq_colors)))
	return (uniq_colors, group_lists)


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default='image.jpg', help="Path to the image")
ap.add_argument("--scale_factor", default=0.5, help="Scale Factor", type=float)
ap.add_argument("-o", "--file_out", default='', help="Path to the image")
# ap.add_argument("--save_roi", default=False, help="Save ROI as roi.json", type=float)
# ap.add_argument("--use_roi_json", default=True, help="Use ROI from roi.json", type=float)

args = vars(ap.parse_args())

# load the image, clone it, and setup the mouse callback function
image = cv2.imread(args["image"])
scale_factor = args["scale_factor"]
width = int(image.shape[1] * scale_factor)
height = int(image.shape[0] * scale_factor)
image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
clone = image.copy()
cv2.namedWindow("image")
# cv2.setMouseCallback("image", on_click)

# keep looping until the 'q' key is pressed
prompt = "Press a to add points, s to save to json, l to load from json, r to reset all points, g to analysis colour group"
roi_pts = []
while True:
	# display the image and wait for a keypress
	cv2.imshow("image", image)
	key = cv2.waitKey(1) & 0xFF
	# if the 'r' key is pressed, reset the cropping region
	if key == ord("r"):
		image = clone.copy()
		roi_pts = []
		print(prompt)

	# 'a' key to add points by selection
	if key == ord("a"):
		new_pts = select_2d_points_array(image)
		if new_pts == None:
			print("Selection canceled")
		roi_pts += new_pts
		draw_points(image, new_pts)
		print("Selection Complete. New Points are: ", new_pts)
		print("Total number of selected points = {}".format(len(roi_pts)))
		print(prompt)


	if key == ord("s"):
		with open("roi.json", "w") as f:
			f.write(json.dumps(roi_pts))
		print("roi.json Saved")
		print(prompt)

	if key == ord("l"):
		image = clone.copy()
		roi_pts = []
		with open("roi.json", "r") as f:
			roi_pts = json.load(f)
		draw_points(image, roi_pts)
		print("roi.json Loaded")
		print(prompt)

	if key == ord("g"):
		uniq_colors, group_lists = group_colors(clone, roi_pts)
		if len(uniq_colors) == len(group_lists):
			filename = args["file_out"]
			if filename == '':
				filename = args["image"].split('.')[0] + '.json'
			dict = {'uniq_colors' : uniq_colors, 'group_lists':group_lists}
			with open(filename, "w") as f:
				f.write(json.dumps(dict))
			print("{} Saved".format(filename))

	# if the 'q' key is pressed, break from the loop
	elif key == ord("q"):
		break


# close all open windows
cv2.destroyAllWindows()
