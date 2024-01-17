import math
import numpy as np
import cv2

class CvHelper:
    @staticmethod
    def calculate_euclidean_distance(point1: tuple, point2: tuple) -> float:
        """
        Calculates the Euclidean distance between two points in a 2-dimensional space.

        Parameters:
        - point1 (tuple): A tuple representing the coordinates (x, y) of the first point.
        - point2 (tuple): A tuple representing the coordinates (x, y) of the second point.

        Returns:
        - float: The Euclidean distance between the two points.
        """
        x1, y1 = point1
        x2, y2 = point2

        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance

    @staticmethod
    def calculate_angle(line1, line2):
        """
        Calculate the angle (in degrees) between two lines defined by two sets of points.

        Parameters:
        - line1 (list of tuples): A list containing two tuples representing the endpoints of the first line.
        - line2 (list of tuples): A list containing two tuples representing the endpoints of the second line.

        Returns:
        - float: The angle between the two lines in degrees.
        """
        # Convert lines to numpy arrays
        line1 = np.array(line1)
        line2 = np.array(line2)

        # Calculate the vectors corresponding to the lines
        vector1 = line1[1] - line1[0]
        vector2 = line2[1] - line2[0]

        # Calculate the dot product and cross product of the vectors
        dot_product = np.dot(vector1, vector2)
        cross_product = np.cross(vector1, vector2)

        # Calculate the magnitudes of the vectors
        magnitude1 = np.linalg.norm(vector1)
        magnitude2 = np.linalg.norm(vector2)

        # Calculate the cosine of the angle between the vectors
        cosine_theta = np.abs(dot_product) / (magnitude1 * magnitude2)

        # Determine the sign of the dot product to determine the direction
        angle_radians = np.arccos(cosine_theta)

        # Determine the sign of the cross product to determine the orientation
        orientation = np.sign(cross_product)

        # Print intermediate results (for debugging)
        # print(dot_product, cross_product)

        # Calculate the angle in degrees
        angle_degrees_bckp = np.degrees(angle_radians)
        # print(angle_degrees_bckp)
        # print(orientation)

        # Determine the final angle considering the direction and orientation
        if dot_product > 0:
            angle_radians = np.arccos(cosine_theta)
            # Convert the angle to degrees
            angle_degrees = 180 - np.degrees(angle_radians)
            # Adjust angle for the cross product sign
            if orientation < 0:
                angle_degrees = 360 - angle_degrees
            if cross_product < 0:
                if orientation < 0:
                    if angle_degrees_bckp > 45:
                        # print("bad")
                        angle_degrees = angle_degrees_bckp
        else:
            angle_radians = np.arccos(cosine_theta)
            # Convert the angle to degrees
            angle_degrees = np.degrees(angle_radians)
            if orientation < 0:
                angle_degrees = 180 - angle_degrees

        return angle_degrees

    @staticmethod
    def rotate_coordinates(points, angle, center=(0, 0)):
        """
        Rotate a set of coordinates around a specified center.

        Parameters:
        - points: A list of (x, y) coordinates to be rotated.
        - angle: The rotation angle in degrees.
        - center: The center of rotation. Default is (0, 0).

        Returns:
        - Rotated coordinates as a numpy array.
        """
        angle_rad = np.radians(angle)
        cos_theta = np.cos(angle_rad)
        sin_theta = np.sin(angle_rad)

        # Translate to the origin, rotate, and translate back
        centered_points = np.array(points) - np.array(center)
        rotated_points = np.dot(centered_points, np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]]))
        rotated_points += np.array(center)

        return rotated_points



    @staticmethod
    def rotate_frame_tracked_points(point_0_a, point_0_b, point_1_b, point_2_b, point_3_b):
        """
        Rotate a set of tracked points based on a reference point and a calculated angle.

        Parameters:
        - point_0_a (tuple): Coordinates of the reference point.
        - point_0_b (tuple): Coordinates of the first tracked point.
        - point_1_b (tuple): Coordinates of the second tracked point.
        - point_2_b (tuple): Coordinates of the third tracked point.
        - point_3_b (tuple): Coordinates of the fourth tracked point.

        Returns:
        - np.ndarray: An array containing the rotated coordinates of the tracked points.
        """
        # Create a new point along a horizontal line with the first point
        marker = (point_0_a[0] + 100, point_0_a[1])

        # Calculate the angle of rotation using CvHelper.calculate_angle function
        shift_angle = CvHelper.calculate_angle(
            (
                point_0_a, point_0_b
            ),
            (
                point_0_a, marker
            )
        )
        # print(shift_angle)

        # Rotate points using CvHelper.rotate_coordinates function
        rotated_points = CvHelper.rotate_coordinates([point_0_b, point_1_b, point_2_b, point_3_b], (180 - shift_angle) * -1,
                                                     point_0_a)

        # Shift points to central zero
        rotated_points[:, 0] = rotated_points[:, 0] - rotated_points[0, 0]
        rotated_points[:, 1] = rotated_points[:, 1] - rotated_points[0, 1]

        return rotated_points

    @staticmethod
    def calculate_vector_direction(point1, point2):
        return np.array(point2) - np.array(point1)

    @staticmethod
    def add_text_to_frame(frame, text, position=(30, 30), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.2, color=(0, 255, 0), thickness=2):
        """
        Add text to a frame.

        Parameters:
        - frame (numpy.ndarray): Input frame.
        - text (str): Text to be added to the frame.
        - position (tuple): Position of the text (x, y).
        - font (int): Font type.
        - font_scale (float): Font scale.
        - color (tuple): Text color (B, G, R).
        - thickness (int): Text thickness.

        Returns:
        - numpy.ndarray: Frame with added text.
        """
        frame_with_text = frame.copy()
        cv2.putText(frame_with_text, text, position, font, font_scale, color, thickness)
        return frame_with_text

    @staticmethod
    def find_intersection(p1, p2, q1, q2):
        """
        Find the intersection point of two line segments defined by points (p1, p2) and (q1, q2).

        Parameters:
        - p1, p2: Tuple representing the coordinates of the first line segment (x, y).
        - q1, q2: Tuple representing the coordinates of the second line segment (x, y).

        Returns:
        - Tuple: Coordinates (x, y) of the intersection point, or None if the lines are parallel.
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = q1
        x4, y4 = q2

        # Calculate determinant to check if lines are parallel
        det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if det != 0:
            # Calculate intersection point coordinates using Cramer's rule
            px = int(((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / det)
            py = int(((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / det)
            return px, py
        else:
            # Lines are parallel, no intersection point
            return None



    @staticmethod
    def segment_marker_by_color(frame_tmp, video_color_metadata):
        """
        Segment markers in a frame based on color information.

        Parameters:
        - frame_tmp: A frame in the CIELAB color model from the OpenCV function.
        - video_color_metadata: Dictionary containing color metadata for segmentation.

        Returns:
        Tuple of binary masks for different color points.
        """

        # Extract color channels
        L_channel = frame_tmp[:, :, 0]
        a_channel = frame_tmp[:, :, 1]
        b_channel = frame_tmp[:, :, 2]

        # Color segmentation using NumPy array operations
        mask_of_points_0 = (a_channel > video_color_metadata["point_0"]["a_down"]) & \
                           (a_channel < video_color_metadata["point_0"]["a_up"]) & \
                           (b_channel > video_color_metadata["point_0"]["b_down"]) & \
                           (b_channel < video_color_metadata["point_0"]["b_up"]) # points 0

        mask_of_points_1 = (a_channel > video_color_metadata["point_1"]["a_down"]) & \
                           (a_channel < video_color_metadata["point_1"]["a_up"]) & \
                           (b_channel > video_color_metadata["point_1"]["b_down"]) & \
                           (b_channel < video_color_metadata["point_1"]["b_up"])  # points 1

        mask_of_points_2 = (a_channel > video_color_metadata["point_2"]["a_down"]) & \
                           (a_channel < video_color_metadata["point_2"]["a_up"]) & \
                           (b_channel > video_color_metadata["point_2"]["b_down"]) & \
                           (b_channel < video_color_metadata["point_2"]["b_up"])  # points 2

        mask_of_points_3 = (a_channel > video_color_metadata["point_3"]["a_down"]) & \
                           (a_channel < video_color_metadata["point_3"]["a_up"]) & \
                           (b_channel > video_color_metadata["point_3"]["b_down"]) & \
                           (b_channel < video_color_metadata["point_3"]["b_up"])  # points 3

        # Dilate masks to enhance segmentation
        kernel = np.ones((5, 5), np.uint8)
        mask_of_points_0 = cv2.dilate(np.uint8(mask_of_points_0 * 255), kernel, iterations=1)
        mask_of_points_1 = cv2.dilate(np.uint8(mask_of_points_1 * 255), kernel, iterations=1)
        mask_of_points_1 = cv2.dilate(np.uint8(mask_of_points_1 * 255), kernel, iterations=1)
        mask_of_points_2 = cv2.dilate(np.uint8(mask_of_points_2 * 255), kernel, iterations=1)
        mask_of_points_3 = cv2.dilate(np.uint8(mask_of_points_3 * 255), kernel, iterations=1)

        return mask_of_points_0, mask_of_points_1, mask_of_points_2, mask_of_points_3

    @staticmethod
    def line_padding(point_per_mask_1, point_per_mask_2, line_pad):
        # Calculate points for the line based on the direction vector and line padding
        direction = CvHelper.calculate_vector_direction(point_per_mask_1,point_per_mask_2)
        point1 = (
            int(point_per_mask_2[0] - line_pad * direction[0]),
            int(point_per_mask_2[1] - line_pad * direction[1]),
        )
        point2 = (
            int(point_per_mask_1[0] + line_pad * direction[0]),
            int(point_per_mask_1[1] + line_pad * direction[1]),
        )
        return point1, point2


    @staticmethod
    def store_video(frames, output_path, fps):
        # Function to store the video with updated frames
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        height, width, _ = frames[0].shape
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for frame in frames:
            out.write(frame)

        out.release()