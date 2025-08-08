#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
import yaml
import os
import math

class AutoNavigator(Node):
    def __init__(self):
        super().__init__('auto_navigator')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, pose: PoseStamped):
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('NavigateToPose action server not available')
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        send_goal_future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected')
            return False

        get_result_future = goal_handle.get_result_async()
        self.get_logger().info('Goal accepted, waiting result...')
        rclpy.spin_until_future_complete(self, get_result_future)
        result = get_result_future.result()
        # result.status codes: check for SUCCEEDED (GoalStatus.STATUS_SUCCEEDED == 4)
        if result.status == 4:
            self.get_logger().info('Goal succeeded')
            return True
        else:
            self.get_logger().warn(f'Goal result: {result.status}')
            return False


def load_waypoints(file_path):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    poses = []
    for p in data.get('waypoints', []):
        ps = PoseStamped()
        ps.header.frame_id = 'map'
        ps.pose.position.x = float(p['x'])
        ps.pose.position.y = float(p['y'])
        ps.pose.position.z = 0.0
        yaw = float(p.get('yaw', 0.0))
        cy = math.cos(yaw/2.0)
        sy = math.sin(yaw/2.0)
        ps.pose.orientation.w = cy
        ps.pose.orientation.z = sy
        poses.append(ps)
    return poses


def main(args=None):
    rclpy.init(args=args)
    node = AutoNavigator()
    wp_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'waypoints.yaml')
    wp_file = os.path.abspath(wp_file)
    if not os.path.exists(wp_file):
        node.get_logger().error(f'Waypoints file not found: {wp_file}')
        return
    waypoints = load_waypoints(wp_file)
    for idx, pose in enumerate(waypoints):
        node.get_logger().info(f"Sending waypoint {idx+1}/{len(waypoints)}: ({pose.pose.position.x}, {pose.pose.position.y})")
        ok = node.send_goal(pose)
        if not ok:
            node.get_logger().warn('Failed to reach waypoint. Stopping.')
            break
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()