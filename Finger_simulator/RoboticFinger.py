import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.optimize import minimize

class RoboticFinger:
    def __init__(self, bone_lengths, fixed_base_angle=-np.pi/2, joint_limits=None):
        """
        Initialize the RoboticFinger instance.

        Parameters:
        - bone_lengths: List of lengths for each bone [L1, L2, L3, L4].
                        L1 is the fixed palm bone.
        - fixed_base_angle: The fixed angle of the palm bone (in radians).
                            Default is -pi/2 (pointing along negative y-axis).
        - joint_limits: List of tuples specifying the (min, max) angles for each joint.
                        If None, defaults to [(-pi/2, pi/2)] for each joint.
        """
        self.L1, self.L2, self.L3, self.L4 = bone_lengths
        self.theta1_fixed = fixed_base_angle
        self.x0, self.y0 = 0.0, 0.0  # Base of the palm bone (fixed)
        self.compute_fixed_base_position()
        self.joint_angles = []
        self.joint_positions = []
        if joint_limits is None:
            self.joint_limits = [(-np.pi/2, np.pi/2) for _ in range(3)]
        else:
            self.joint_limits = joint_limits

    def compute_fixed_base_position(self):
        """Compute the position of the fixed palm bone (L1)."""
        self.x1 = self.x0 + self.L1 * np.cos(self.theta1_fixed)
        self.y1 = self.y0 + self.L1 * np.sin(self.theta1_fixed)

    def forward_kinematics(self, q):
        """
        Compute the forward kinematics for the moving joints.

        Parameters:
        - q: Array of joint angles [theta2, theta3, theta4].

        Returns:
        - x4, y4: Coordinates of the fingertip.
        """
        theta2, theta3, theta4 = q
        # Positions of the moving joints and fingertip
        theta_total_2 = self.theta1_fixed + theta2
        theta_total_3 = theta_total_2 + theta3
        theta_total_4 = theta_total_3 + theta4

        x2 = self.x1 + self.L2 * np.cos(theta_total_2)
        y2 = self.y1 + self.L2 * np.sin(theta_total_2)
        x3 = x2 + self.L3 * np.cos(theta_total_3)
        y3 = y2 + self.L3 * np.sin(theta_total_3)
        x4 = x3 + self.L4 * np.cos(theta_total_4)
        y4 = y3 + self.L4 * np.sin(theta_total_4)
        return np.array([x4, y4])

    def inverse_kinematics(self, x_target, y_target, initial_guess):
        """
        Perform inverse kinematics to find the joint angles for a given target position.

        Parameters:
        - x_target, y_target: Coordinates of the target position.
        - initial_guess: Initial guess for the joint angles.

        Returns:
        - q_solution: Array of joint angles [theta2, theta3, theta4], or None if failed.
        """
        # Objective function to minimize
        def objective_function(q):
            fk = self.forward_kinematics(q)
            position_error = np.linalg.norm(fk - np.array([x_target, y_target]))
            regularization = 0.1 * np.sum(q**2)
            return position_error + regularization

        # Use the joint limits from the instance
        joint_limits = self.joint_limits

        # Optimization to solve inverse kinematics
        result = minimize(objective_function, initial_guess, method='SLSQP', bounds=joint_limits)

        if result.success:
            return result.x
        else:
            return None

    def perform_inverse_kinematics(self, x_d, y_d):
        """
        Perform inverse kinematics for each point in the trajectory.

        Parameters:
        - x_d, y_d: Arrays of x and y coordinates of the desired trajectory.
        """
        # Start with an initial guess within the joint limits
        initial_guess = np.array([
            (self.joint_limits[0][0] + self.joint_limits[0][1]) / 2,
            (self.joint_limits[1][0] + self.joint_limits[1][1]) / 2,
            (self.joint_limits[2][0] + self.joint_limits[2][1]) / 2,
        ])  # Midpoint of joint limits

        for x_t, y_t in zip(x_d, y_d):
            q_solution = self.inverse_kinematics(x_t, y_t, initial_guess)
            if q_solution is not None:
                self.joint_angles.append(q_solution)
                initial_guess = q_solution  # Update initial guess

                # Compute joint positions for visualization
                theta2, theta3, theta4 = q_solution
                theta_total_2 = self.theta1_fixed + theta2
                theta_total_3 = theta_total_2 + theta3
                theta_total_4 = theta_total_3 + theta4

                x2 = self.x1 + self.L2 * np.cos(theta_total_2)
                y2 = self.y1 + self.L2 * np.sin(theta_total_2)
                x3 = x2 + self.L3 * np.cos(theta_total_3)
                y3 = y2 + self.L3 * np.sin(theta_total_3)
                x4 = x3 + self.L4 * np.cos(theta_total_4)
                y4 = y3 + self.L4 * np.sin(theta_total_4)

                self.joint_positions.append([[self.x0, self.x1, x2, x3, x4],
                                             [self.y0, self.y1, y2, y3, y4]])
            else:
                print(f"Inverse kinematics failed at target ({x_t:.2f}, {y_t:.2f}), skipping this point.")
                # Append the last valid joint position and angles
                if self.joint_positions:
                    self.joint_positions.append(self.joint_positions[-1])
                else:
                    # If no valid positions yet, append initial position
                    self.joint_positions.append([[self.x0, self.x1], [self.y0, self.y1]])
                if self.joint_angles:
                    self.joint_angles.append(self.joint_angles[-1])
                else:
                    self.joint_angles.append(initial_guess)
                # Keep the same initial guess

    def animate_finger(self, x_d, y_d, x_workspace, y_workspace):
        """
        Create an animation of the finger drawing the trajectory over the workspace.

        Parameters:
        - x_d, y_d: Arrays of x and y coordinates of the desired trajectory.
        - x_workspace, y_workspace: Arrays of x and y coordinates of the workspace points.
        """
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        ax.grid(True)

        # Plot the reachable workspace
        ax.scatter(x_workspace, y_workspace, s=1, c='lightblue', alpha=0.5, label='Reachable Workspace')

        # Plot the desired trajectory
        ax.plot(x_d, y_d, 'r--', label='Desired Trajectory')

        # Initialize line for the finger
        line, = ax.plot([], [], 'b.-', linewidth=2, markersize=8, label='Finger')

        # Set plot limits based on workspace
        ax.set_xlim(min(x_workspace) - 0.1, max(x_workspace) + 0.1)
        ax.set_ylim(min(y_workspace) - 0.1, max(y_workspace) + 0.1)

        # Initialize the animation
        def init():
            line.set_data([], [])
            return line,

        # Update function for the animation
        def animate(i):
            x_points = self.joint_positions[i][0]
            y_points = self.joint_positions[i][1]
            line.set_data(x_points, y_points)
            return line,

        # Create the animation
        anim = FuncAnimation(fig, animate, init_func=init,
                             frames=len(self.joint_positions), interval=50, blit=True)

        ax.legend()
        plt.title('Robotic Finger Drawing Trajectory over Reachable Workspace')
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.show()

def deg_to_rad(degrees):
    """Convert degrees to radians."""
    return degrees * np.pi / 180.0

def flower_trajectory(k=5, a=1, scale=0.1, x_center=0, y_center=0, num_points=100):
    """
    Generates x and y coordinates for a 2D flower trajectory (rose curve) with adjustable center and size.

    Parameters:
    - k (int): Determines the number of petals. If k is odd, the rose has k petals; if even, 2k petals.
    - a (float): Amplitude of the curve.
    - scale (float): Scaling factor to adjust the overall size of the trajectory.
    - x_center (float): x-coordinate of the center of the trajectory.
    - y_center (float): y-coordinate of the center of the trajectory.
    - num_points (int): Number of points to compute along the curve.

    Returns:
    - x (ndarray): x-coordinates of the trajectory.
    - y (ndarray): y-coordinates of the trajectory.
    """
    theta = np.linspace(0, 2 * np.pi, num_points)
    r = a * np.cos(k * theta) * scale
    x = r * np.cos(theta) + x_center
    y = r * np.sin(theta) + y_center
    return x, y

def circular_trajectory(radius, center_x, center_y, num_points=100):
    """
    Generate a circular trajectory for the fingertip.

    Parameters:
    - radius: Radius of the circle.
    - center_x, center_y: Coordinates of the circle's center.
    - num_points: Number of points in the trajectory.

    Returns:
    - x_d, y_d: Arrays of x and y coordinates of the trajectory points.
    """
    theta = np.linspace(0, 2 * np.pi, num_points)
    x_d = center_x + radius * np.cos(theta)
    y_d = center_y + radius * np.sin(theta)
    return x_d, y_d

if __name__ == "__main__":
    # Define link lengths: [L1 (fixed palm bone), L2, L3, L4]
    link_lengths = [0.5, 0.4, 0.3, 0.2]

    # Define normal human finger joint ranges of motion
    joint_limits = [
        (deg_to_rad(-90), deg_to_rad(30)),   # Theta2 (MCP Joint)
        (deg_to_rad(-100), deg_to_rad(0)),   # Theta3 (PIP Joint)
        (deg_to_rad(-80), deg_to_rad(20))    # Theta4 (DIP Joint)
    ]

    # Create an instance of RoboticFinger with normal joint limits
    finger = RoboticFinger(link_lengths, fixed_base_angle=-np.pi, joint_limits=joint_limits)

    # Generate the reachable workspace before the simulation

    # Define the joint limits in radians
    theta2_limits = joint_limits[0]  # (theta2_min, theta2_max)
    theta3_limits = joint_limits[1]  # (theta3_min, theta3_max)
    theta4_limits = joint_limits[2]  # (theta4_min, theta4_max)

    # Total number of random samples
    num_samples = 10000  # Adjust for desired resolution and performance

    # Generate random samples of joint angles within their limits
    theta2_samples = np.random.uniform(theta2_limits[0], theta2_limits[1], num_samples)
    theta3_samples = np.random.uniform(theta3_limits[0], theta3_limits[1], num_samples)
    theta4_samples = np.random.uniform(theta4_limits[0], theta4_limits[1], num_samples)

    # Initialize arrays to store fingertip positions
    x_workspace,y_workspace = [],[]

    # Compute the forward kinematics for each combination of joint angles
    for theta2, theta3, theta4 in zip(theta2_samples, theta3_samples, theta4_samples):
        q = np.array([theta2, theta3, theta4])
        x4_y4 = finger.forward_kinematics(q)
        x_workspace.append(x4_y4[0])
        y_workspace.append(x4_y4[1])

    # Generate a trajectory within the finger's reachable workspace
    x_d, y_d = flower_trajectory(k=5, a=1, scale=0.5, x_center=finger.x1 - 0.4, y_center= finger.y1 + 0.5)

    # Perform inverse kinematics to find joint angles
    finger.perform_inverse_kinematics(x_d, y_d)

    # Animate the finger drawing the trajectory over the workspace
    finger.animate_finger(x_d, y_d, x_workspace, y_workspace)

    # Plot joint angles over time
    if finger.joint_angles:
        # Convert joint angles to degrees for easier interpretation
        joint_angles_degrees = np.rad2deg(finger.joint_angles)
        joint_angles_degrees = np.array(joint_angles_degrees)
        time_steps = np.arange(len(joint_angles_degrees))

        plt.figure()
        plt.plot(time_steps, joint_angles_degrees[:, 0], label='Theta2 (MCP Joint)')
        plt.plot(time_steps, joint_angles_degrees[:, 1], label='Theta3 (PIP Joint)')
        plt.plot(time_steps, joint_angles_degrees[:, 2], label='Theta4 (DIP Joint)')

        plt.xlabel('Time Step')
        plt.ylabel('Joint Angle (degrees)')
        plt.title('Joint Angles Over Time')
        plt.legend()
        plt.grid(True)
        plt.show()
