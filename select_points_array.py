import cv2
# Selection for 2D array: Ask for (1) first list first item, (2) first listlast item, (3) last list first item
# Interpolate between the input


def select_2d_points_array(image):
    mode = 0
    first_list = []
    second_list = []
    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            point = [x, y]
            if mode == 0:
                first_list.append(point)
            elif mode ==1:
                second_list.append(point)
            print(point)

    cv2.setMouseCallback("image", on_click)

    # Wait till user made three selection
    print("Select all items in the first list, press 'a' when done. 'q' to cancel")
    while (True):
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return None
        if key == ord("a"):
            if mode == 0:
                mode = 1
                print("Select first items in the other lists, press 'a' when done. 'q' to cancel")
            elif mode == 1:
                print("Total {} points X {} lists".format(len(first_list),len(second_list) + 1) )
                lists = [first_list]

                if len(first_list) == 0:
                    return None
                very_first_pt_x = first_list[0][0]
                very_first_pt_y = first_list[0][1]
                for first_point in second_list:
                    points = []
                    for point in first_list:
                        x = point[0]
                        y = point[1]
                        points.append([x -  very_first_pt_x + first_point[0], y - very_first_pt_y + first_point[1]])
                    lists.append(points)
                return lists
