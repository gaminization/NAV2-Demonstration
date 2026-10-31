from glob import glob

from setuptools import setup

package_name = "nav2-demo"
py_package_name = "nav2_demo"

setup(
    name=package_name,
    version="0.1.0",
    packages=[py_package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/config/qos", glob("config/qos/*.yaml")),
        ("share/" + package_name + "/maps", glob("maps/*.yaml") + glob("maps/*.pgm")),
    ],
    install_requires=["setuptools", "pyyaml"],
    tests_require=["pytest"],
    zip_safe=True,
    maintainer="Garv Arora",
    maintainer_email="66058398+gaminization@users.noreply.github.com",
    description="TurtleBot3 + Nav2 demo with switchable Gazebo worlds, QoS, bags and security options.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "mission_server = nav2_demo.mission_server:main",
            "mission_client = nav2_demo.mission_client:main",
            "nav_goal = nav2_demo.nav_goal:main",
            "world_info = nav2_demo.world_info:main",
            "explorer = nav2_demo.explorer:main",
            "dynamic_obstacles = nav2_demo.dynamic_obstacles:main",
            "policy_filter = nav2_demo.policy_tools:main",
        ],
    },
)
