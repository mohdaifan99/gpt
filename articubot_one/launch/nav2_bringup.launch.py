from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    pkg_dir = os.path.dirname(__file__)
    params_file = os.path.join(pkg_dir, '..', 'params', 'nav2_params.yaml')
    map_file = '/home/ubuntu/maps/josh_map.yaml'  # change to your map path

    ld = LaunchDescription()

    # static transform base->laser
    ld.add_action(Node(
        package='tf2_ros', executable='static_transform_publisher', name='base_to_laser',
        arguments=['0.0','0.0','0.12','0','0','0','base_link','laser']
    ))

    ld.add_action(Node(
        package='nav2_map_server', executable='map_server', name='map_server',
        parameters=[{'yaml_filename': map_file}], output='screen'))

    ld.add_action(Node(
        package='nav2_amcl', executable='amcl', name='amcl',
        parameters=[params_file], output='screen'))

    ld.add_action(Node(
        package='nav2_controller', executable='controller_server', name='controller_server',
        parameters=[params_file], output='screen'))

    ld.add_action(Node(
        package='nav2_planner', executable='planner_server', name='planner_server',
        parameters=[params_file], output='screen'))

    ld.add_action(Node(
        package='nav2_recoveries', executable='recoveries_server', name='recoveries_server',
        parameters=[params_file], output='screen'))

    ld.add_action(Node(
        package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator',
        parameters=[params_file], output='screen'))

    ld.add_action(Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager',
        parameters=[{'use_sim_time': False, 'autostart': True,
                     'node_names': ['map_server','amcl','planner_server','controller_server','bt_navigator','recoveries_server']}],
        output='screen'))

    return ld