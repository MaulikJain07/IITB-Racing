import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class VCU_NODE(Node):

    def __init__(self):
        super().__init__('VCU')
        self.subscription = self.create_subscription(String,'AI2VCU',self.listener_callback,10)
        self.subscription  # prevent unused variable warning

        self.publisher_ = self.create_publisher(String, 'VCU2AI', 10) 
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0


    def listener_callback(self, msg):
        self.get_logger().info('Confirmation: "%s"' % msg.data)



    def timer_callback(self):
        msg = String()
        msg.data = 'AI, Can you hear me?: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Asking: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    VCU = VCU_NODE()

    rclpy.spin(VCU)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    VCU.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()