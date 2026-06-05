TIAGo Library Navigation and QR Scanning Project

This package contains the ROS files for Group 3 TTTC2343 TIAGo library simulation.

Week 9 content:
- Gazebo library world
- Map files
- Multi-point navigation
- UI for destination selection and robot status

Week 10 content:
- QR code scanning task
- Bookshelf 2 Right QR station
- QR scanner node using pyzbar
- QR result published to /qr_scan_result

Main launch:
roslaunch tiago_library_nav multi_point_navigation.launch

QR-only launch:
roslaunch tiago_library_nav qr_task.launch

Install QR dependencies in Docker:
bash scripts/install_qr_dependencies.sh
