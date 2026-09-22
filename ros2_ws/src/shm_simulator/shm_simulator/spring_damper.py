from std_srvs.srv import Trigger   # for perturbation
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point,Vector3
from rcl_interfaces.msg import SetParametersResult

class DampedSHM(Node):
    def __init__(self):
        super().__init__('damped_shm_node')  # this is the node name...


        # ---Creating a service to change the values of k and c---
        # the string will be the name of the parameter. 
        self.declare_parameter("stiffness",5.0)   # spring const
        self.declare_parameter("damping_c", 0.5)  # damping const  
        self.declare_parameter("kick", 5.0) # perturbation ki value bhi change kar denge via command line. 

        self.k = self.get_parameter("stiffness").value
        self.c = self.get_parameter("damping_c").value
        self.kick_value = self.get_parameter("kick").value

        # below function,automatically jab bhi service call hogi, uski value change kardega.

        self.add_on_set_parameters_callback(self.parameter_callback)

        
        # Physics Parameters
        self.position = 2.0   # 2 meters door start karenge with 0 velocity.
        self.velocity = 0.0
        self.mass = 1.0       # in kg
        
        # Time step (sec) - basically time real life mein continuos flow karta hai, but computer ko ek dt chahiye, har dt baad vo positions and all calculate kare. 
        self.dt = 0.08

        # --- ROS Setup ---
        # try karo ki har object ka different publisher ho.
        self.publisher_origin_ = self.create_publisher(Marker, 'shm_marker_origin', 10) 
        self.publisher_ball_ = self.create_publisher(Marker, 'shm_marker_ball', 10) 
        self.publisher_spring_ = self.create_publisher(Marker, 'shm_marker_spring', 10)  


        self.energy_publisher_ = self.create_publisher(Vector3, 'shm_energy', 10) 


        # I will call this perturbation a kick. 
        self.kick_service = self.create_service(Trigger,'shm_kick',self.apply_kick)
        

        self.timer = self.create_timer(self.dt, self.update_physics)
        self.get_logger().info("SHM Simulator Started") #shuru hone se pehle ka msg

    def update_physics(self):
        # Forces
        f_spring = -self.k * self.position
        f_damping = -self.c * self.velocity
        f_total = f_spring + f_damping

        #Energies
        ke = 0.5 * self.mass * (self.velocity**2)
        pe = 0.5 * self.k * (self.position**2)
        tot_e = ke + pe  
        energy_msg = Vector3()
        energy_msg.x = ke
        energy_msg.y = pe
        energy_msg.z = tot_e 

        # define acceleration
        acc = f_total / self.mass

        # Update Velocity and Position
        self.velocity += acc * self.dt
        self.position += self.velocity * self.dt

        # Publish to RViz
        self.get_logger().info(f'Position: {self.position:.2f}')
        self.publish_marker()
        self.energy_publisher_.publish(energy_msg)

    def publish_marker(self):

        # ---1. The Red Ball ---
        r_ball = Marker()  # A class in ros
        r_ball.header.frame_id = "map"
        r_ball.header.stamp = self.get_clock().now().to_msg()
        
        # Set shape (SPHERE)
        r_ball.type = Marker.SPHERE
        r_ball.id = 0
        
        # Set Scale (meters)
        r_ball.scale.x = 0.5
        r_ball.scale.y = 0.5
        r_ball.scale.z = 0.5

        # Set Color (Red color, non-transparent)
        r_ball.color.r = 1.0
        r_ball.color.g = 0.0
        r_ball.color.b = 0.0
        r_ball.color.a = 1.0

        # Set Position (Moving along X axis) - we want to restrict the motion.
        r_ball.pose.position.x = self.position
        r_ball.pose.position.y = 0.0
        r_ball.pose.position.z = 0.0    

        self.publisher_ball_.publish(r_ball)



        # --- 2. The Green Center Point ---
        origin = Marker()
        origin.header.frame_id = "map"
        origin.header.stamp = self.get_clock().now().to_msg()
        origin.type = Marker.CUBE  # trying new things
        origin.id = 1              # Unique ID hona chahiye of every object
        
        # Size (Make it a tall, thin wall)
        origin.scale.x = 0.1
        origin.scale.y = 0.1
        origin.scale.z = 0.1
        
        # Color (Green)
        origin.color.g = 1.0
        origin.color.a = 1.0
        
        # Position (Fixed at 0,0,0)
        origin.pose.position.x = 0.0
        origin.pose.position.y = 0.0
        origin.pose.position.z = 0.0
        
        self.publisher_origin_.publish(origin)



        # --- 3. The Yellow String (The Spring) ---
        string = Marker()
        string.header.frame_id = "map"
        string.header.stamp = self.get_clock().now().to_msg()
        string.type = Marker.LINE_STRIP
        string.id = 2            # IMPORTANT: Unique ID!
        
        # Line Thickness (sirf x mein hi dimension dene ka fayda hai)
        string.scale.x = 0.05
        
        # Color (Yellow)
        string.color.r = 1.0
        string.color.g = 1.0
        string.color.a = 1.0
        
        # Define the two points of the line
        start_point = Point()  # Start at Wall
        start_point.x = 0.0
        start_point.y = 0.0
        start_point.z = 0.0
        
        end_point = Point()    # End at Ball
        end_point.x = self.position
        end_point.y = 0.0
        end_point.z = 0.0
        
        string.points = [start_point, end_point] # ek array bnata hai of points aur unko color kardeta hai.
        
        self.publisher_spring_.publish(string)


    # --- function to apply kick ---

    def apply_kick(self, request, response):

        # perturbation basically impulse hoga, a sudden change in velocity.

        self.velocity += self.kick_value

        self.get_logger().warn("Perturbation has started. Kick!")

        # ---response ---
        response.success = True
        response.message = f"Kicked with strength {self.kick_value}"
        return response        
    

    # --- function to change the values of k and c.

    def parameter_callback(self, params):  # params is the list of params the user is trying to change.
        
        # we don't need a for loop, we can execute the command one by one, but if we upload a yaml file which commands it to run 2-3 commands simultaneously, then its better to have a for loop.
        
        for param in params:
             
            # Changing value of stiffness/spring constant.

            if param.name == 'stiffness':
                if param.value < 0.0:
                    self.get_logger().warn("Spring const can't be negative.")
                    return SetParametersResult(successful=False)  # it basically tells ROS to reject the value. 
                self.k = param.value
                self.get_logger().info(f"Spring const updated to {self.k}")

            # Changing value of damping coefficient.

            if param.name == 'damping_c':
                if param.value < 0.0:
                    self.get_logger().warn("Damping coeff can't be negative.")
                    return SetParametersResult(successful=False)
                self.k = param.value
                self.get_logger().info(f"Damping Coeff updated to {self.k}")

            if param.name == "kick":
                self.kick_value = param.value
                self.get_logger().info(f"Kick Strength updated to {self.kick_value}")
            
        return SetParametersResult(successful = True)   

def main(args=None):
    rclpy.init(args=args)
    node = DampedSHM()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
