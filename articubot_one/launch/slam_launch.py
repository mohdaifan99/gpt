from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    ld = LaunchDescription()

    # static transform: base_link -> laser (adjust if different frames)
    ld.add_action(Node(
        package='tf2_ros', executable='static_transform_publisher', name='base_to_laser',
        arguments=['0.0','0.0','0.12','0','0','0','base_link','laser']
    ))

    # slam_toolbox: async (online) mapping
    ld.add_action(Node(
        package='slam_toolbox', executable='async_slam_toolbox_node', name='slam_toolbox',
        parameters=[{
            'use_sim_time': False,
            'mode': 'mapping'
        }],
        output='screen'
    ))

    # optional rviz (comment out if not required)
    ld.add_action(Node(
        package='rviz2', executable='rviz2', name='rviz', output='screen'
    ))

    return ld