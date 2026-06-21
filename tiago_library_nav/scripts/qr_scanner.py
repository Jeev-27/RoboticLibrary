#!/usr/bin/env python3

import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
from pyzbar.pyzbar import decode


class QRScanner:
    def __init__(self):
        rospy.init_node("qr_scanner_node")

        self.bridge = CvBridge()

        self.image_sub = rospy.Subscriber(
            "/xtion/rgb/image_raw",
            Image,
            self.image_callback,
            queue_size=1
        )

        self.result_pub = rospy.Publisher(
            "/qr_scan_result",
            String,
            queue_size=10,
            latch=True
        )

        rospy.loginfo("QR Scanner using pyzbar started.")
        rospy.loginfo("Listening to /xtion/rgb/image_raw")
        rospy.loginfo("Publishing result to /qr_scan_result")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

            decoded_objects = decode(frame)

            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")
                rospy.loginfo_throttle(2, "QR CODE DETECTED: {}".format(qr_data))
                self.result_pub.publish(qr_data)

        except Exception as e:
            rospy.logwarn("QR scanner error: {}".format(e))

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    scanner = QRScanner()
    scanner.run()
