TIAGo Library Navigation Package

This package contains the map files, edited Gazebo world, launch file, and Python UI for multi-point navigation.

Deliverables:
1. maps/library_final_fixed_map.pgm
2. maps/library_final_fixed_map.yaml
3. worlds/project_library_final_fixed.world
4. scripts/multi_point_ui.py
5. launch/multi_point_navigation.launch

How to run:

1. Start TIAGo simulation:
roslaunch tiago_gazebo tiago_gazebo.launch public_sim:=true robot:=steel world:=project_library_final_fixed

2. Fix PAL navigation config:
rosrun tiago_library_nav fix_pal_nav_config.sh

3. Run navigation package:
roslaunch tiago_library_nav multi_point_navigation.launch

4. Open RViz:
rviz

5. Set Fixed Frame to map.
6. Use 2D Pose Estimate to set robot starting position.
7. Use the UI to select checkpoint 1, 2, 3, or automatic route.

Notes:
- /scan_raw is relayed to /scan.
- AMCL is used for localization.
- move_base is launched with eband local planner.
- DWA planner was not used because it was not available in the Docker environment.
