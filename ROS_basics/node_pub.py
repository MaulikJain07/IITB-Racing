                # first two imports are necessary...
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32 
from random import randint

class publisher(Node):

    def __init__(self):
        super().__init__('my_pub')
        self.get_logger().info('Yoo! the node is active...')
        self.pub = self.create_publisher(Int32, 'rpm_data', 10) 

        self.timer = self.create_timer(1.0, self.phuncshion)
        self.number = 0

    def phuncshion(self):
        msg = Int32()
        msg.data = self.number
        self.pub.publish(msg)
        self.get_logger().info(f'Publishing RPM: {self.number}')
        self.number = randint(3000,5000)
        

def main(args=None):
    #initialize
    rclpy.init(args=args)

    # defining node object
    node1 = publisher()

    #infinite loop run karta hai...
    rclpy.spin(node1) 

    #clean karne mein help karega after ctrl+C
    node1.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()