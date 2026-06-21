#!/usr/bin/env python3

import rospy
import actionlib
import json
import threading
import time

from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus


class TiagoBookFinder:
    def __init__(self):
        rospy.init_node("tiago_book_finder_node")

        self.status_pub = rospy.Publisher(
            "/book_finder/status",
            String,
            queue_size=10
        )

        self.qr_debug_pub = rospy.Publisher(
            "/book_finder/qr_debug",
            String,
            queue_size=10
        )

        self.busy = False
        self.latest_qr = None
        self.lock = threading.Lock()

        rospy.Subscriber(
            "/book_finder/request",
            String,
            self.request_callback
        )

        rospy.Subscriber(
            "/qr_scan_result",
            String,
            self.qr_callback
        )

        self.move_base = actionlib.SimpleActionClient(
            "move_base",
            MoveBaseAction
        )

        # HOME / Entrance coordinate
        self.home = {
            "name": "Entrance Area",
            "x": 1.16,
            "y": -8.23,
            "z": 0.65,
            "w": 0.76
        }

        # Robot stop locations in front of each QR shelf
        self.bookshelves = {
            1: {"name": "Bookshelf 1", "x": -5.57, "y": 1.12, "z": 0.87, "w": 0.50},
            2: {"name": "Bookshelf 2", "x": -6.57, "y": 1.06, "z": 0.52, "w": 0.85},
            3: {"name": "Bookshelf 3", "x": -5.89, "y": 5.99, "z": -0.88, "w": 0.48},
            4: {"name": "Bookshelf 4", "x": -7.15, "y": 6.06, "z": -0.49, "w": 0.87},
            5: {"name": "Bookshelf 5", "x": 7.30, "y": 2.42, "z": 0.89, "w": 0.46},
            6: {"name": "Bookshelf 6", "x": 6.22, "y": 2.30, "z": 0.52, "w": 0.85},
            7: {"name": "Bookshelf 7", "x": 6.85, "y": 7.05, "z": -0.84, "w": 0.55},
            8: {"name": "Bookshelf 8", "x": 5.86, "y": 7.52, "z": -0.48, "w": 0.88}
        }

        # Catalogue database: this tells TIAGo which shelf to go to directly
        self.shelf_books = {
            1: ["B001", "B002", "B003", "B004"],
            2: ["B005", "B006", "B007", "B008"],
            3: ["B009", "B010", "B011", "B012"],
            4: ["B013", "B014", "B015", "B016"],
            5: ["B017", "B018", "B019", "B020"],
            6: ["B021", "B022", "B023", "B024"],
            7: ["B025", "B026", "B027", "B028"],
            8: ["B029", "B030", "B031", "B032"]
        }

        self.book_catalog = {}
        for shelf_id, books in self.shelf_books.items():
            for book in books:
                self.book_catalog[book] = shelf_id

        self.publish_status("Waiting for move_base action server...")
        self.move_base.wait_for_server()
        self.publish_status("Book finder backend ready. Waiting for HTML request.")

    def publish_status(self, text):
        rospy.loginfo(text)
        self.status_pub.publish(String(data=text))

    def publish_qr_debug(self, text):
        rospy.loginfo(text)
        self.qr_debug_pub.publish(String(data=text))

    def qr_callback(self, msg):
        with self.lock:
            self.latest_qr = msg.data.strip()

        self.publish_qr_debug("QR detected raw data: {}".format(msg.data.strip()))

    def request_callback(self, msg):
        book_id = msg.data.strip().upper()

        if not book_id:
            self.publish_status("ERROR: Empty Book ID received.")
            return

        if self.busy:
            self.publish_status("WARN: Robot is busy. Please wait until current mission finishes.")
            return

        self.busy = True

        mission_thread = threading.Thread(
            target=self.run_mission,
            args=(book_id,)
        )
        mission_thread.daemon = True
        mission_thread.start()

    def send_goal(self, location):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()

        goal.target_pose.pose.position.x = location["x"]
        goal.target_pose.pose.position.y = location["y"]
        goal.target_pose.pose.position.z = 0.0

        goal.target_pose.pose.orientation.x = 0.0
        goal.target_pose.pose.orientation.y = 0.0
        goal.target_pose.pose.orientation.z = location["z"]
        goal.target_pose.pose.orientation.w = location["w"]

        self.publish_status(
            "Navigating to {} | x={:.2f}, y={:.2f}".format(
                location["name"],
                location["x"],
                location["y"]
            )
        )

        self.move_base.send_goal(goal)
        self.move_base.wait_for_result()

        state = self.move_base.get_state()

        if state == GoalStatus.SUCCEEDED:
            self.publish_status("Arrived at {}.".format(location["name"]))
            return True

        self.publish_status(
            "ERROR: Failed to reach {}. move_base state={}".format(
                location["name"],
                state
            )
        )
        return False

    def scan_target_shelf(self, requested_book, target_shelf):
        with self.lock:
            self.latest_qr = None

        self.publish_status("Scanning QR at Bookshelf {} for 10 seconds...".format(target_shelf))

        start_time = time.time()
        timeout_sec = 10.0

        while time.time() - start_time < timeout_sec and not rospy.is_shutdown():
            with self.lock:
                qr_text = self.latest_qr

            if qr_text:
                try:
                    data = json.loads(qr_text)
                    qr_shelf = int(data.get("bookshelf", -1))
                    books = data.get("books", [])

                    self.publish_qr_debug(
                        "Bookshelf {} QR contains books: {}".format(
                            qr_shelf,
                            ", ".join(books)
                        )
                    )

                    if qr_shelf != target_shelf:
                        self.publish_status(
                            "WARNING: Detected Bookshelf {} QR, but expected Bookshelf {}.".format(
                                qr_shelf,
                                target_shelf
                            )
                        )
                        return False

                    if requested_book in books:
                        self.publish_status(
                            "SUCCESS: Book {} is available at Bookshelf {}.".format(
                                requested_book,
                                target_shelf
                            )
                        )
                        return True

                    self.publish_status(
                        "NOT AVAILABLE: Book {} should be at Bookshelf {}, but the QR list does not contain it.".format(
                            requested_book,
                            target_shelf
                        )
                    )
                    return False

                except Exception as e:
                    self.publish_qr_debug("QR detected but could not parse JSON: {}".format(qr_text))
                    self.publish_qr_debug("Parse error: {}".format(e))

            time.sleep(0.5)

        self.publish_status("NOT_FOUND: No valid QR detected at Bookshelf {}.".format(target_shelf))
        return False

    def run_mission(self, requested_book):
        self.publish_status("Received request for Book ID: {}".format(requested_book))

        if requested_book not in self.book_catalog:
            self.publish_status(
                "CATALOG ERROR: Book {} is not registered in the library catalogue.".format(
                    requested_book
                )
            )
            self.busy = False
            return

        target_shelf = self.book_catalog[requested_book]
        self.publish_status(
            "Catalogue lookup: Book {} should be located at Bookshelf {}.".format(
                requested_book,
                target_shelf
            )
        )

        reached = self.send_goal(self.bookshelves[target_shelf])

        if reached:
            self.scan_target_shelf(requested_book, target_shelf)
        else:
            self.publish_status(
                "Mission failed: TIAGo could not reach Bookshelf {}.".format(
                    target_shelf
                )
            )

        self.publish_status("Returning to entrance area...")
        returned_home = self.send_goal(self.home)

        if returned_home:
            self.publish_status("Mission completed. TIAGo is back at entrance area.")
        else:
            self.publish_status("Mission completed, but TIAGo failed to return to entrance area.")

        self.busy = False


if __name__ == "__main__":
    try:
        node = TiagoBookFinder()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
