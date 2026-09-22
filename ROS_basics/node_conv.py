import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Float32

class converter(Node):
    def __init__(self):
        super().__init__('Converter')
        self.sub = self.create_subscription(Int32, 'rpm_data', self.callback, 10)
        self.pub = self.create_publisher(Float32, 'wheel_speed', 10)
        # self.timer = self.create_timer(1.0, self.callback)

    def callback(self,msg):
        wheel_speed = Float32()
        wheel_speed.data = msg.data*0.015
        self.pub.publish(wheel_speed)
        self.get_logger().info(f'Wheel speed: {wheel_speed.data}')

def main(args=None):

    #initialize
    rclpy.init(args=args)

    # defining node object
    node = converter()

    #infinite loop run karta hai...
    rclpy.spin(node) 

    #clean karne mein help karega after ctrl+C
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
    