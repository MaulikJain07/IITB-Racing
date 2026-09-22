# ROS imports
import rclpy
from rclpy.node import Node

# variable type imports
from sensor_msgs.msg import PointCloud, PointCloud2
from std_msgs.msg import Header
import sensor_msgs_py.point_cloud2 as pc2
from geometry_msgs.msg import PoseArray, Pose
from visualization_msgs.msg import Marker, MarkerArray

# mathematical tools
import numpy as np
from sklearn.linear_model import RANSACRegressor
from rclpy.qos import qos_profile_sensor_data
from sklearn.cluster import DBSCAN

# Lifetime import
from builtin_interfaces.msg import Duration

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('cone_detector')
        
        self.sub = self.create_subscription(PointCloud, 'carmaker/pointcloud', self.pc_callback,qos_profile_sensor_data)

        self.pub = self.create_publisher(PointCloud2, '/filtered_cones', 1)

        self.centroid_pub = self.create_publisher(PoseArray, '/centroids', 1)

        self.marker_pub = self.create_publisher(MarkerArray, '/cone_markers', 1)

    def pc_callback(self, msg):

        # Converting pointcloud data into numpy matrix.

        points_list = []
        for point in msg.points:
            x = point.x
            y = point.y
            z = point.z
            list = [x,y,z]
            points_list.append(list)
            
        cloud_matrix = np.array(points_list)
        

        # self.get_logger().info(f'BINGO! Caught a matrix of shape: {cloud_matrix.shape}')


        # RANSAC

        XY = cloud_matrix[:,:2]
        Z = cloud_matrix[:,2]

        ransac = RANSACRegressor(residual_threshold=0.02)
        ransac.fit(XY,Z)
        ground = ransac.inlier_mask_

        # Defining cone matrix from cloud matrix by subtracting ground.
        cone_matrix = cloud_matrix[~ground]  


        # DBSCAN - clustering
        XY_cones = cone_matrix[:,:2]
        clustering = DBSCAN(eps=0.3, min_samples=3).fit(XY_cones)
        labels = clustering.labels_

        # Cluster karke unka centroid aage publish karenge
        centroids=[]
        for i in range(max(labels)+1):
            points_this_cone = cone_matrix[labels == i]
            center = np.mean(points_this_cone,axis=0)
            centroids.append(center)

        new_header = Header()  # header contains timestamp and frame id.
        new_header.stamp = self.get_clock().now().to_msg()
        new_header.frame_id = 'Lidar_F'

        cone_msg = pc2.create_cloud_xyz32(new_header, cone_matrix)
        self.pub.publish(cone_msg)

        # self.get_logger().info(f' Points to RviZ2 {len(cone_matrix)}')
        self.get_logger().info(f'{len(centroids)} cones detected in the frame.')

        

        pose_array = PoseArray()
        pose_array.header.stamp = self.get_clock().now().to_msg()
        pose_array.header.frame_id = 'Lidar_F'
        
        for center in centroids:
            pose = Pose()
            # We must cast NumPy floats back to standard Python floats for ROS
            pose.position.x = float(center[0])
            pose.position.y = float(center[1])
            pose.position.z = float(center[2])
            pose.orientation.w = 1.0 # Valid quaternion requirement
            pose_array.poses.append(pose)
            
        self.centroid_pub.publish(pose_array)


        # Publishing marker array to visualise the clustered cones as cylinders in rviz

        marker_array = MarkerArray()
        for i, center in enumerate(centroids):
            marker = Marker()
            marker.header.frame_id = 'Lidar_F'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'cones'
            marker.id = i
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            
            # Position
            marker.pose.position.x = float(center[0])
            marker.pose.position.y = float(center[1])
            marker.pose.position.z = float(center[2])
            marker.pose.orientation.w = 1.0

            # Lifetime
            marker.lifetime = Duration(sec=0,nanosec = 110000000)
            
            # Scale (Make it look like a physical cone)
            marker.scale.x = 0.2  # 20cm wide
            marker.scale.y = 0.2  # 20cm deep
            marker.scale.z = 0.3  # 30cm tall
            
            # Color (Neon Green)
            marker.color.r = 0.0
            marker.color.g = 1.0
            marker.color.b = 0.0
            marker.color.a = 1.0 # Alpha (1.0 is fully solid)
            
            marker_array.markers.append(marker)
            
        self.marker_pub.publish(marker_array)

def main(args=None):

    rclpy.init(args=args)
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()