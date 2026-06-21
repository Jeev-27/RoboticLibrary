cmake_minimum_required(VERSION 3.0.2)
project(tiago_library_nav)

find_package(catkin REQUIRED COMPONENTS
  rospy
  geometry_msgs
  nav_msgs
  actionlib_msgs
  move_base_msgs
  actionlib
  sensor_msgs
  std_msgs
  cv_bridge
  image_transport
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/multi_point_ui.py
  scripts/qr_scanner.py
  scripts/book_finder_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch maps worlds scripts
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
