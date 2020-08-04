import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path
from cobowl.robot import CollaborativeRobotInterface
from cobot_msgs.msg import Command
from cobot_msgs.srv import ReachCartesianPose, Grasp, MoveGripper, NamedTarget
from std_srvs.srv import Trigger

class RealCollaborativeRobot(Node, CollaborativeRobotInterface):

    def __init__(self, knowledge_base_path, user_folder):
        Node.__init__(self, 'real_robot')
        CollaborativeRobotInterface.__init__(self, knowledge_base_path, user_folder)
        self.move_to = self.create_client(ReachCartesianPose, '/go_to_cartesian_goal')
        self.grasp = self.create_client(Grasp, '/grasp')
        self.reach_named_target = self.create_client(NamedTarget, '/move_to')
        self.release = self.create_client(MoveGripper, '/move_gripper')
        self.reset = self.create_client(Trigger, '/reset')
        self.sub = self.create_subscription(Command, '/plan_request', self.run, 10)
        ### TODO: remove test objects
        self.world.add_object("peg")  # Manually create an object or testing purposes

    def say_hello(self, commands):
        self.prompt_welcome(commands)
        self.introduce_itself(commands)

    def prompt_welcome(self, commands):
        print()
        print("PANDA PLATFORM INTERFACE")
        print("========================")
        print()
        print("To command the robot use one of the following trigger words:")
        for cmd in commands:
            print("- {}".format(cmd))

    def introduce_itself(self, commands):
        pass

    def pre_notify(self, task):
        print("About to perform {}".format(task))

    def post_notify(self, task):
        print("{} completed".format(task))

    def send_command(self, command_msg):
        print("Received command: ", command_msg)
        action = command_msg.action
        target = command_msg.targets
        self.world.send_command(action, target)

    def move_operator(self, target):
        def move_to():
            req = ReachCartesianPose.Request()
            print("_use_move_operator {}...".format(target))
            req.type = 0 if target[0].name == "storage" else 1  # else target.name = "handover"
            # TODO:retrieve from KB
            print(req)
            self.move_to.call_async(req)
            print("plan moving on")
        return move_to

    def close_operator(self, target):
        def grasp():
            req = Grasp.Request()
            req.width = 2.0  # [cm]
            req.force = 50.0  # [N]
            print("Grasping {}...".format(target))
            self.grasp.call_async(req)
        return grasp

    def open_operator(self):
        def release():
            req = MoveGripper.Request()
            req.width = 8.0
            self.release.call_async(req)
        return release

    def idle_operator(self):
        def wait():
            print("Waiting...")
        return wait

    def stop_operator(self):
        def stop():
            print("Stopping...")
        return stop

    def reset_operator(self):
        def reset():
            req = Trigger.Request()
            self.reset.call_async(req)
            self.reload_knowledge()
            req = NamedTarget.Request()
            req.name = 'ready'
            self.reach_named_target.call_async(req)
            self.world.add_object("peg")
        return reset

    def handle_anchoring_error(self, object):
        print("REACH FINAL STAGE OF ERROR")
        print("COULD NOT ANCHOR", object)

def main(args=None):
    rclpy.init(args=args)
    RESOURCE_PATH = get_package_share_directory('cobot_knowledge')
    kb_path = str(Path(RESOURCE_PATH)/ 'handover.owl')
    user_kb_path = str(Path(RESOURCE_PATH) / 'user_defined')
    node = RealCollaborativeRobot(kb_path, user_kb_path)

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
