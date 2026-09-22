import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'first_robo'
    urdf_file_name = 'my_robot.urdf'

    # Find the path to your package
    pkg_share = get_package_share_directory(package_name)
    
    # Path to the URDF file
    default_model_path = os.path.join(pkg_share, 'urdf', urdf_file_name)

    # Node 1: Robot State Publisher (Reads URDF and publishes tf)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['cat ', default_model_path])}]
    )

    # Node 2: Joint State Publisher GUI (Allows you to move joints)
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    # Node 3: Rviz2 (Visualizer)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
