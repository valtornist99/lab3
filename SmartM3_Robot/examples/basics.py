import os
import random
from datetime import datetime

from smart_m3.m3_kp_api import *


class KP_Handler:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        # in case if you want to react on added/removed data - just use self.kp.your_function(....) here
        print('Agent_X reporting: {}'.format(datetime.now()))
        print('    added', added)
        print('    removed', removed)

        for data in added:
            if str(data[1]) == 'trash_value':
                print("!!! KP_sub_reaction !!! Garbage in the smart space :(")
                break

        for data in removed:
            if str(data[1]) == 'trash_value':
                print("!!! KP_sub_reaction !!! Some garbage was removed! :)")
                break


if __name__ == '__main__':
    kp = m3_kp_api()  # connection to the smart space, PrintDebug=True parameter will print debug messages

    # this condition means that kp will listen all data in the smart space
    subscription_triple = Triple(None, None, None)
    handler = KP_Handler(kp)
    # this is how we create subscription at certain triple pattern in the smart space
    handler_subscription = kp.load_subscribe_RDF(subscription_triple, handler)

    insert_list = [
        Triple(URI('Agent_X'), URI('has_temperature'), Literal(10)),
        Triple(URI('Agent_X'), URI('wind_speed_measurement'), Literal(2.34)),
        Triple(URI('Agent_X'), URI('wind_direction'), Literal('SW')),
        Triple(URI('Agent_X'), URI('send_data'), URI('Agent_Y')),
    ]

    # insert example
    print('---Insert example---')
    kp.load_rdf_insert(insert_list)

    # query example - agent try to get information about Object=URI('Agent_Y')
    print('---Query example---')
    kp.load_query_rdf(Triple(None, None, URI('Agent_Y')))
    print('Query result about Agent_Y in the smart space: {}'.format(kp.result_rdf_query))

    # update example - the weather became warmer - so Agent_X need to update information about it
    # 1. Search for the weather triplet from Agent_X
    # 2. If we successfully find data - replace it!
    print('---Update example---')

    kp.load_query_rdf(Triple(URI('Agent_X'), URI('has_temperature'), None))
    if len(kp.result_rdf_query) > 0:
        new_triples = []
        for old_triple in kp.result_rdf_query:
            new_triples.append(Triple(old_triple[0], old_triple[1], Literal(random.randint(-10, 20))))

        # N.B! If you want to update only one triple - you still need to make wrapping around array
        # kp.load_rdf_update([Triple(...)], [Triple(...)])
        kp.load_rdf_update(new_triples, kp.result_rdf_query)

    # remove example
    # Create 'trash' triplets for Agent_X and Agent_Y and delete Agent_X 'trash' triples afterwards
    # also, if kp meets 'trash_value' predicate - he will send information about it
    print('---Remove example---')

    trash_triples = []
    for i in range(0, 10):
        trash_triples.append(Triple(URI('Agent_X') if i % 2 == 0 else URI('Agent_Y'), URI('trash_value'),
                                    Literal(random.randint(-10, 20))))

    # insert and remove
    kp.load_rdf_insert(trash_triples)
    kp.load_rdf_remove(Triple(URI('Agent_X'), URI('trash_value'), None))

    # check 'trash' triples which are left in the smart space
    kp.load_query_rdf(Triple(None, URI('trash_value'), None))
    print('Trash triples in the smart space: {}'.format(kp.result_rdf_query))

    # unsubscribe from any data from the smart space
    kp.load_unsubscribe(handler_subscription)

    # remove all data from Smart Space by applying Triplet(None, None, None)
    kp.clean_sib()

    # if you want to see how subscription handler show information about sib cleaning,
    # you need to add sleep(...) function BEFORE kp.leave(), because leave will cut down connection with broker

    # sleep(5) # main thread will sleep 5 seconds and subscription thread will be able to do something

    kp.leave()

    # Unfortunately, subscription threads will work after kp.leave and block main program.
    # So, it's okay just to send 0 signal manually
    raise os._exit(0)
