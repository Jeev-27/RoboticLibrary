# TIAGo Library Navigation and QR Scanning Project

This ROS package contains the Group 3 TIAGo library simulation project for TTTC2343 Sistem Robot Cerdas.

## Project Summary

The project demonstrates a customised TIAGo robot simulation in a library environment. It includes:

- Gazebo library world
- SLAM-generated map files
- Multi-point autonomous navigation
- UI-based destination selection
- Robot status display
- QR code scanning task at the Bookshelf 2 - Right station

Week 9 focuses on mapping, multi-point navigation and UI development. Week 10 extends the project by adding a QR scanning task using TIAGo's RGB camera.

## Package Structure

```text
tiago_library_nav/
├── package.xml
├── CMakeLists.txt
├── launch/
│   ├── multi_point_navigation.launch
│   └── qr_task.launch
├── scripts/
│   ├── multi_point_ui.py
│   ├── qr_scanner.py
│   ├── fix_pal_nav_config.sh
│   └── install_qr_dependencies.sh
├── maps/
│   ├── library_final_fixed_map.pgm
│   └── library_final_fixed_map.yaml
├── worlds/
│   ├── project_library_final_fixed.world
│   └── project_library_week10_qr.world
├── qrcodes/
│   ├── Entrance Area.png
│   ├── Table Area 1 - Left.png
│   ├── Table Area 2 - Right.png
│   ├── Table Area 3.png
│   ├── Bookshelf 1 - Left.png
│   └── Bookshelf 2 - Right.png
└── task_models/
    └── qr_bookshelf_right/
```

## Important Notes

- The navigation system uses `/scan_raw` relayed to `/scan`.
- AMCL is used for localisation.
- `move_base` is launched with the `eband` local planner.
- DWA is not used because it was not available in the Docker environment.
- QR scanning uses `pyzbar`, not OpenCV `QRCodeDetector`, because the container OpenCV may not have QUIRC QR decoding enabled.

## How to Run

### 1. Start Docker

```bash
xhost +local:docker
xhost +local:root

docker run -it --rm \
--name tiago_tutorial \
--gpus all \
--net=host \
--privileged \
--device=/dev/dri:/dev/dri \
--env="DISPLAY=$DISPLAY" \
--env="QT_X11_NO_MITSHM=1" \
--env="NVIDIA_VISIBLE_DEVICES=all" \
--env="NVIDIA_DRIVER_CAPABILITIES=all" \
--volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
--volume="$HOME/Downloads:/host_downloads:rw" \
palroboticssl/tiago_tutorials:noetic
```

Inside Docker:

```bash
source /opt/ros/noetic/setup.bash
source /tiago_public_ws/devel/setup.bash
```

### 2. Copy package into workspace and build

```bash
rm -rf /tiago_public_ws/src/tiago_library_nav
cp -r /host_downloads/tiago_library_nav /tiago_public_ws/src/

cd /tiago_public_ws
catkin build tiago_library_nav
source /tiago_public_ws/devel/setup.bash
rospack profile
```

### 3. Install QR dependencies

```bash
bash /tiago_public_ws/src/tiago_library_nav/scripts/install_qr_dependencies.sh
```

### 4. Copy Week 10 world into TIAGo Gazebo worlds folder

```bash
mkdir -p /tiago_public_ws/src/tiago_simulation/tiago_gazebo/worlds

cp /tiago_public_ws/src/tiago_library_nav/worlds/project_library_week10_qr.world \
/tiago_public_ws/src/tiago_simulation/tiago_gazebo/worlds/project_library_week10_qr.world
```

### 5. Terminal 1: Start TIAGo simulation

```bash
roslaunch tiago_gazebo tiago_gazebo.launch \
public_sim:=true \
robot:=steel \
world:=project_library_week10_qr
```

### 6. Terminal 2: Run navigation, UI and QR scanner

```bash
docker exec -it tiago_tutorial bash
source /opt/ros/noetic/setup.bash
source /tiago_public_ws/devel/setup.bash

bash /tiago_public_ws/src/tiago_library_nav/scripts/fix_pal_nav_config.sh
roslaunch tiago_library_nav multi_point_navigation.launch
```

### 7. Terminal 3: Open RViz

```bash
docker exec -it tiago_tutorial bash
source /opt/ros/noetic/setup.bash
source /tiago_public_ws/devel/setup.bash
rviz
```

RViz setup:

- Fixed Frame: `map`
- Add: Map, RobotModel, TF, LaserScan, Odometry, Path, PoseArray
- Map topic: `/map`
- LaserScan topic: `/scan`
- Odometry topic: `/mobile_base_controller/odom`
- Use `2D Pose Estimate` before sending goals.

### 8. Terminal 4: View camera

```bash
docker exec -it tiago_tutorial bash
source /opt/ros/noetic/setup.bash
source /tiago_public_ws/devel/setup.bash
rqt_image_view
```

Select:

```text
/xtion/rgb/image_raw
```

### 9. Terminal 5: Check QR result

```bash
docker exec -it tiago_tutorial bash
source /opt/ros/noetic/setup.bash
source /tiago_public_ws/devel/setup.bash
rostopic echo /qr_scan_result
```

Use the UI and choose:

```text
6 - Bookshelf 2 - Right
```

The QR scanner should publish the detected QR data to `/qr_scan_result`.

## Week 10 Demo Video Checklist

Record:

1. Gazebo world with QR board at Bookshelf 2 - Right.
2. TIAGo robot in the library world.
3. RViz map, RobotModel and localisation.
4. UI menu.
5. Select `6 - Bookshelf 2 - Right`.
6. rqt_image_view showing the QR code through `/xtion/rgb/image_raw`.
7. Terminal showing `/qr_scan_result` output.

