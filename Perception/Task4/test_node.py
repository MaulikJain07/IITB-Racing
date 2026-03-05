import rclpy
from rclpy.node import Node

class test1_node(Node):
    def __init__(self):
        super().__init__('TEST')
        self.get_logger().info('Hello! Hi I am printed when this node is active.')

class test2_node(Node):
    def __init__(self):
        super().__init__('TEST2')
        self.get_logger().info('Hello! Lets see if this msg prints or not.')


def main(args=None):

    #initialize
    rclpy.init(args=args)

    # defining node object
    node1 = test1_node()
    node2 = test2_node()

    #infinite loop run karta hai...
    rclpy.spin(node1) 
    rclpy.spin(node2)

    #clean karne mein help karega after ctrl+C
    node1.destroy_node()
    node2.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()