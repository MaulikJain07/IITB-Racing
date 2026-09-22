import rclpy 
from rclpy.node import Node
from std_msgs.msg import Int32

class subscriber(Node):
    
    def __init__(self):
        super().__init__('my_sub')

        # Syntax: (MessageType, 'topic_name', callback_function, queue_size)
        self.sub = self.create_subscription(Int32, 'rpm_data', self.conphirm, 10)

        # THIS IS THE CALLBACK: It runs automatically EVERY time a message arrives
    def conphirm(self,msg):
        if msg.data>=4500:
            self.get_logger().warn(f"DANGER, RPM too high!")
        else:
            self.get_logger().info(f'{msg.data} RPM received.')

def main():
    rclpy.init()
    node = subscriber()
    rclpy.spin(node) # This keeps the node alive, waiting for messages
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()