import launch
import launch.actions
import launch.substitutions
import launch_ros.actions
import os

def generate_launch_description():
    myenv = os.environ
    myenv["PYTHONUNBUFFERED"] = "1"

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            'node_prefix',
            default_value=[launch.substitutions.EnvironmentVariable('USER'), '_'],
            description='Prefix for node names'),

        launch_ros.actions.Node(
            package='cobot_planner', node_executable='real_robot', output='screen', env=myenv,
            node_name=[launch.substitutions.LaunchConfiguration('node_prefix'), 'real_robot']),

        launch_ros.actions.Node(
            package='cobot_nlp', node_executable='listener', output='screen', env=myenv,
            node_name=[launch.substitutions.LaunchConfiguration('node_prefix'), 'listener']),

    ])
