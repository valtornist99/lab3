import random
import time
from smart_m3.m3_kp_api import *

robotID = "robot_1"
auxRobotID = "aux_" + robotID

def askForTarget(kp):
    kp.load_rdf_remove(Triple(URI("goal_" + auxRobotID), URI("is"), URI("find_target")))
    kp.load_rdf_insert(Triple(URI("goal_" + auxRobotID), URI("is"), URI("find_target")))

def move(target_coordinate, kp):
    kp.load_query_rdf(Triple(URI("robot_coordinate_" + robotID), URI("is"), None))
    res = kp.result_rdf_query
    robot_coordinate = int(str(res[0][2]))
    distance = target_coordinate - robot_coordinate
    time.sleep(random.randint(1, 5))
    print(robotID + " moved " + str(distance) + " meters")
    new_robot_coordinate = robot_coordinate + distance
    kp.load_rdf_remove(Triple(URI("robot_coordinate_" + robotID), URI("is"), None))
    kp.load_rdf_insert(Triple(URI("robot_coordinate_" + robotID), URI("is"), Literal(new_robot_coordinate)))

def shoot(kp):
    time.sleep(random.randint(1, 5))
    print(robotID + " turned around")
    print(robotID + " shot")
    print(robotID + " turned around")
    kp.load_rdf_remove(Triple(URI("goal_" + auxRobotID), URI("is"), URI("evaluate_shot")))
    kp.load_rdf_insert(Triple(URI("goal_" + auxRobotID), URI("is"), URI("evaluate_shot")))

def end(kp):
    print(robotID + " finished!")
    kp.load_rdf_remove(Triple(URI(robotID), URI("has_been_reached"), URI("end_of_track")))
    kp.load_rdf_insert(Triple(URI(robotID), URI("has_been_reached"), URI("end_of_track")))

class Target_Handler:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        for data in added:
            coordinate = int(str(data[2]))
            move(coordinate, kp)
            shoot(kp)


class EndOfTrack_Handler:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        for data in added:
            coordinate = int(str(data[2]))
            move(coordinate, kp)
            end(kp)


class Shot_Handler:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        for data in added:
            askForTarget(kp)

if __name__ == '__main__':
    kp = m3_kp_api(PrintDebug=True)

    kp.load_rdf_insert(Triple(URI("robot_coordinate_" + robotID), URI("is"), Literal(0)))

    subscription_triple = Triple(URI("target_coordinate_" + robotID), URI("is"), None)
    handler_target = Target_Handler(kp)
    handler_subscription1 = kp.load_subscribe_RDF(subscription_triple, handler_target)

    subscription_triple = Triple(URI("end_of_track_coordinate_" + robotID), URI("is"), None)
    handler_endOfTrack = EndOfTrack_Handler(kp)
    handler_subscription2 = kp.load_subscribe_RDF(subscription_triple, handler_endOfTrack)

    subscription_triple = Triple(URI("shot_" + robotID), URI("is"), URI("evaluated"))
    handler_shot = Shot_Handler(kp)
    handler_subscription3 = kp.load_subscribe_RDF(subscription_triple, handler_shot)

    time.sleep(3)
    askForTarget(kp)
    time.sleep(600)

    kp.load_unsubscribe(handler_subscription1)
    kp.load_unsubscribe(handler_subscription2)
    kp.load_unsubscribe(handler_subscription3)

    kp.clean_sib()
    kp.leave()
