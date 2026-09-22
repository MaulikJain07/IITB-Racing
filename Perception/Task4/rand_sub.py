import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Pose
from rclpy.qos import qos_profile_sensor_data

class subscriber_cone(Node):

    def __init__(self):

        super().__init__('cone_receiver')
        self.sub = self.create_subscription(PoseArray, '/centroids', self.callback, qos_profile_sensor_data)

    def callback(self,msg):
        num_cones = len(msg.poses)

        if num_cones == 0:
            self.get_logger().warn(f'No cones detected!')
            return
        
        coords = [(round(pose.position.x, 2), round(pose.position.y, 2)) for pose in msg.poses]

        self.get_logger().info(f'--- Frame update: {num_cones} cones ---')
        self.get_logger().info(f'Locations (X, Y): {coords}')


def main():
    rclpy.init()
    node = subscriber_cone()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()