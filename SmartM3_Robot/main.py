from threading import Thread
import random
import time
from smart_m3.m3_kp_api import *

robotID = "robot_1"
auxRobotID = "aux_" + robotID

targetCoordinates = [10, 20, 35, 45]
curTarget = 0

hits = 0
timer = 0
timerStopped = True

def StartTimer():
    global timer
    while True:
        if not timerStopped:
            time.sleep(1)
            timer += 1
timer_thread = Thread(target=StartTimer, args=())

def findTarget(kp):
    global curTarget
    global timer_thread
    global timerStopped

    if not timer_thread.is_alive():
        timer_thread.start()

    timerStopped = True
    print("time: " + str(timer))

    time.sleep(random.randint(1, 5))
    if curTarget != len(targetCoordinates) - 1:
        kp.load_rdf_remove(Triple(URI("target_coordinate_" + robotID), URI("is"), None))
        kp.load_rdf_insert(Triple(URI("target_coordinate_" + robotID), URI("is"), Literal(targetCoordinates[curTarget])))
    else:
        kp.load_rdf_remove(Triple(URI("end_of_track_coordinate_" + robotID), URI("is"), None))
        kp.load_rdf_insert(Triple(URI("end_of_track_coordinate_" + robotID), URI("is"), Literal(targetCoordinates[curTarget])))
    curTarget += 1

    timerStopped = False

def evaluateShot(kp):
    global hits
    global timerStopped
    timerStopped = True
    print("time: " + str(timer))

    time.sleep(random.randint(1, 5))
    hit = random.randint(0, 1)
    hits += hit

    kp.load_rdf_remove(Triple(URI("shot_" + robotID), URI("is"), URI("evaluated")))
    kp.load_rdf_insert(Triple(URI("shot_" + robotID), URI("is"), URI("evaluated")))

    timerStopped = False

def end(kp):
    global timerStopped
    timerStopped = True

    kp.load_rdf_remove(Triple(URI("hits_result_" + robotID), URI("is"), None))
    kp.load_rdf_insert(Triple(URI("hits_result_" + robotID), URI("is"), Literal(hits)))

    kp.load_rdf_remove(Triple(URI("time_result_" + robotID), URI("is"), None))
    kp.load_rdf_insert(Triple(URI("time_result_" + robotID), URI("is"), Literal(timer)))

    print("Send result:" + str(hits) + ", " + str(timer))


class Target_Handler:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        for data in added:
            findTarget(kp)


class Evaluation_Handler:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        for data in added:
            evaluateShot(kp)


class EndOfTrack_Handler:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        time.sleep(3)
        for data in added:
            end(kp)


if __name__ == '__main__':
    kp = m3_kp_api(PrintDebug=True)

    subscription_triple = Triple(URI("goal_" + auxRobotID), URI("is"), URI("find_target"))
    handler_target = Target_Handler(kp)
    handler_subscription1 = kp.load_subscribe_RDF(subscription_triple, handler_target)

    subscription_triple = Triple(URI("goal_" + auxRobotID), URI("is"), URI("evaluate_shot"))
    handler_evaluation = Evaluation_Handler(kp)
    handler_subscription2 = kp.load_subscribe_RDF(subscription_triple, handler_evaluation)

    subscription_triple = Triple(URI(robotID), URI("has_been_reached"), URI("end_of_track"))
    handler_endOfTrack = EndOfTrack_Handler(kp)
    handler_subscription3 = kp.load_subscribe_RDF(subscription_triple, handler_endOfTrack)

    input("...")

    kp.load_unsubscribe(handler_subscription1)
    kp.load_unsubscribe(handler_subscription2)
    kp.load_unsubscribe(handler_subscription3)

    kp.clean_sib()
    kp.leave()
