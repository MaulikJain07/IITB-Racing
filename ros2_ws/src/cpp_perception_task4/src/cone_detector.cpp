#include <memory> // Needed for shared pointers

// The C++ equivalent of 'import rclpy'
#include "rclcpp/rclcpp.hpp" 

// The C++ equivalent of 'from sensor_msgs.msg import PointCloud'
#include "sensor_msgs/msg/point_cloud.hpp" 

// std::placeholders allows us to pass variables into our callback
using std::placeholders::_1; 

class PerceptionNode : public rclcpp::Node 
{
public:
    // This is the __init__ function
    PerceptionNode() : Node("cone_detector_cpp") 
    {
        // 1. Setup the "Best Effort" QoS profile for sensor data
        rclcpp::QoS qos_profile = rclcpp::SensorDataQoS();

        // 2. Create the Subscriber
        // Notice the ugly std::bind stuff? That's just how C++ connects the callback function.
        subscription_ = this->create_subscription<sensor_msgs::msg::PointCloud>(
            "/carmaker/pointcloud", 
            qos_profile, 
            std::bind(&PerceptionNode::pc_callback, this, _1)
        );
        
        RCLCPP_INFO(this->get_logger(), "C++ Node is alive and listening...");
    }

private:
    // This is your pc_callback function!
    // Notice it receives a SharedPtr (a memory address), not the raw message itself.
    void pc_callback(const sensor_msgs::msg::PointCloud::SharedPtr msg) const 
    {
        // Because 'msg' is a pointer, we use the arrow '->' instead of a dot '.' to read it
        size_t num_points = msg->points.size();
        
        // The C++ equivalent of self.get_logger().info()
        RCLCPP_INFO(this->get_logger(), "BINGO! Caught a cloud with %zu points!", num_points);
    }

    // Declare the subscription variable
    rclcpp::Subscription<sensor_msgs::msg::PointCloud>::SharedPtr subscription_;
};

int main(int argc, char * argv[]) 
{
    rclcpp::init(argc, argv);
    
    // Spin the node (keeps it alive)
    rclcpp::spin(std::make_shared<PerceptionNode>());
    
    rclcpp::shutdown();
    return 0;
}