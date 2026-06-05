#!/usr/bin/env python3

import rospy
import math
import time
from geometry_msgs.msg import PoseStamped
from actionlib_msgs.msg import GoalStatusArray
from nav_msgs.msg import Odometry

status_text = "Waiting for goal"
latest_status_code = -1
current_position = None

# ============================================================
# CHECKPOINT LIST
# IMPORTANT:
# Replace the x and y values with your real RViz coordinates.
# Use RViz 2D Nav Goal, then:
# rostopic echo -n 1 /move_base_simple/goal
# to get the selected x and y position.
# ============================================================

CHECKPOINTS = {
    "1": {
        "name": "Entrance Area",
        "x": 1.10,
        "y": -8.22,
        "yaw": 0.0
    },
    "2": {
        "name": "Table Area 1 - Left",
        "x": -5.43,
        "y": -5.90,
        "yaw": 0.0
    },
    "3": {
        "name": "Table Area 2 - Right",
        "x": 7.18,
        "y": -5.47,
        "yaw": 0.0
    },
    "4": {
        "name": "Table Area 3",
        "x": 0.05,
        "y": 4.15,
        "yaw": 0.0
    },
    "5": {
        "name": "Bookshelf 1 - Left",
        "x": -6.36,
        "y": 3.75,
        "yaw": 0.0
    },
    "6": {
        "name": "Bookshelf 2 - Right",
        "x": 6.49,
        "y": 4.55,
        "yaw": 0.0
    }
}


def yaw_to_quaternion(yaw):
    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)
    return qz, qw


def status_callback(msg):
    global status_text, latest_status_code

    if len(msg.status_list) == 0:
        status_text = "No goal sent yet"
        latest_status_code = -1
        return

    latest_status_code = msg.status_list[-1].status

    if latest_status_code == 0:
        status_text = "Pending: goal received"
    elif latest_status_code == 1:
        status_text = "Active: robot is moving to destination"
    elif latest_status_code == 2:
        status_text = "Preempted: goal was cancelled or replaced"
    elif latest_status_code == 3:
        status_text = "Success: destination reached"
    elif latest_status_code == 4:
        status_text = "Aborted: robot failed to reach destination"
    elif latest_status_code == 5:
        status_text = "Rejected: goal was rejected"
    elif latest_status_code == 8:
        status_text = "Recalled: goal was cancelled before execution"
    else:
        status_text = "Status code: {}".format(latest_status_code)


def odom_callback(msg):
    global current_position
    current_position = msg.pose.pose.position


def send_goal(pub, checkpoint):
    goal = PoseStamped()
    goal.header.frame_id = "map"
    goal.header.stamp = rospy.Time.now()

    goal.pose.position.x = checkpoint["x"]
    goal.pose.position.y = checkpoint["y"]
    goal.pose.position.z = 0.0

    qz, qw = yaw_to_quaternion(checkpoint["yaw"])
    goal.pose.orientation.z = qz
    goal.pose.orientation.w = qw

    pub.publish(goal)


def show_status():
    print("\n========== ROBOT STATUS ==========")
    print("Status:", status_text)

    if current_position is not None:
        print("Current position:")
        print("  x = {:.2f}".format(current_position.x))
        print("  y = {:.2f}".format(current_position.y))
    else:
        print("Current position: not available yet")

    print("==================================\n")


def print_checkpoints():
    print("\n========== CHECKPOINT COORDINATES ==========")
    for key, value in CHECKPOINTS.items():
        print("{} - {} | x = {:.2f}, y = {:.2f}, yaw = {:.2f}".format(
            key,
            value["name"],
            value["x"],
            value["y"],
            value["yaw"]
        ))
    print("============================================\n")


def print_menu():
    print("\n======================================")
    print("      TIAGo Multi-Point Navigation UI")
    print("======================================")
    print("Choose destination:")
    print("1 - Entrance Area")
    print("2 - Table Area 1 - Left")
    print("3 - Table Area 2 - Right")
    print("4 - Table Area 3")
    print("5 - Bookshelf 1 - Left")
    print("6 - Bookshelf 2 - Right")
    print("a - Automatic route: 1 -> 2 -> 3 -> 4 -> 5 -> 6")
    print("c - Show checkpoint coordinates")
    print("s - Show robot status")
    print("q - Quit")
    print("======================================")


def wait_until_goal_finished(timeout_sec=120):
    start_time = time.time()

    while not rospy.is_shutdown():
        show_status()

        if latest_status_code == 3:
            print("Destination reached.\n")
            return True

        if latest_status_code == 4:
            print("Navigation aborted. The path may be blocked.\n")
            return False

        if latest_status_code == 5:
            print("Goal rejected.\n")
            return False

        if time.time() - start_time > timeout_sec:
            print("Timeout. Robot did not reach the destination in time.\n")
            return False

        time.sleep(2)


def main():
    rospy.init_node("tiago_multi_point_navigation_ui")

    goal_pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=1)

    rospy.Subscriber("/move_base/status", GoalStatusArray, status_callback)
    rospy.Subscriber("/mobile_base_controller/odom", Odometry, odom_callback)

    rospy.sleep(1.0)

    print("\nTIAGo Navigation UI started.")
    print("Make sure these are running:")
    print("1. TIAGo Gazebo simulation")
    print("2. /scan_raw to /scan relay")
    print("3. map_server")
    print("4. AMCL")
    print("5. move_base with eband")
    print("6. RViz")
    print("\nBefore sending goals, set 2D Pose Estimate in RViz.\n")

    while not rospy.is_shutdown():
        print_menu()
        choice = input("Enter your choice: ").strip().lower()

        if choice in CHECKPOINTS:
            selected = CHECKPOINTS[choice]

            print("\nSelected destination:", selected["name"])
            print("Sending goal: x = {}, y = {}, yaw = {}".format(
                selected["x"],
                selected["y"],
                selected["yaw"]
            ))

            send_goal(goal_pub, selected)
            wait_until_goal_finished()

        elif choice == "a":
            print("\nStarting automatic route:")
            print("Entrance Area -> Table Area 1 -> Table Area 2 -> Table Area 3 -> Bookshelf 1 -> Bookshelf 2")

            for key in ["1", "2", "3", "4", "5", "6"]:
                selected = CHECKPOINTS[key]

                print("\nSending robot to:", selected["name"])
                print("Goal: x = {}, y = {}, yaw = {}".format(
                    selected["x"],
                    selected["y"],
                    selected["yaw"]
                ))

                send_goal(goal_pub, selected)
                success = wait_until_goal_finished()

                if not success:
                    print("Automatic route stopped because robot failed to reach:", selected["name"])
                    break

            print("Automatic route finished or stopped.\n")

        elif choice == "c":
            print_checkpoints()

        elif choice == "s":
            show_status()

        elif choice == "q":
            print("Exiting TIAGo Navigation UI.")
            break

        else:
            print("Invalid input. Please choose 1, 2, 3, 4, 5, 6, a, c, s, or q.")


if __name__ == "__main__":
    main()
