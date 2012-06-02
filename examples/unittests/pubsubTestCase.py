import os
import sys
import time
import unittest

sys.path.append('../..')

import spade
from xmpp.simplexml import Node

host = "127.0.0.1"

class SubscribeBehaviour(spade.Behaviour.EventBehaviour):
    
    def _process(self):
        msg = self._receive(True)
        self.myAgent.eventmsg = msg

class PubSubTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.Aaid = spade.AID.aid("a@"+host,["xmpp://a@"+host])
        self.Baid = spade.AID.aid("b@"+host,["xmpp://b@"+host])

    	self.a = spade.Agent.Agent("a@"+host, "secret")
    	self.a.wui.start()
    	self.a.start()
    	self.b = spade.Agent.Agent("b@"+host, "secret")
    	self.b.wui.start()
    	self.b.start()
    	
    	self.a.setSocialItem('b@'+host)
        self.a._socialnetwork['b@'+host].subscribe()
        self.b.setSocialItem('a@'+host)
        self.b._socialnetwork['a@'+host].subscribe()
        
        self.a.deleteEvent("ExistsNode")
        self.b.deleteEvent("ExistsNode")
        self.a.deleteEvent("NENode")
        self.b.deleteEvent("NENode")
    	
    def tearDown(self):
        self.a.deleteEvent("ExistsNode")
        self.b.deleteEvent("ExistsNode")
        self.a.deleteEvent("NENode")
        self.b.deleteEvent("NENode")
        self.a.stop()
        self.b.stop()

    def testSubscribeNotExistEvent(self):
        result = self.a.subscribeToEvent("NENode")
        self.assertEqual(result, ('error', ['item-not-found']) )
        
    def testUnsubscribeNotExistEvent(self):
        result = self.a.unsubscribeFromEvent("NENode")
        self.assertEqual(result, ('error', ['item-not-found']) )
    
    def testDeleteNotExistEvent(self):
        result = self.a.deleteEvent("NENode")
        self.assertEqual(result, ('error', ['item-not-found']) )

    def testPublishNotExistEvent(self):
        result = self.a.publishEvent('NENode', Node(tag='foo'))
        self.assertEqual(result[0], 'ok')
        self.assertEqual(len(result[1]), 2)
        self.assertEqual(result[1][0], 'NENode')
        self.assertEqual(type(result[1][1]), unicode)

        self.a.deleteEvent("NENode")
        
    def testCreateEvent(self):
        result = self.a.createEvent("ExistsNode")
        self.assertEqual(result, ('ok', ['ExistsNode']))
        
        self.a.deleteEvent("ExistsNode")
        
    def testPublishEvent(self):
        
        result = self.a.createEvent("ExistsNode")
        self.assertEqual(result, ('ok', ['ExistsNode']))
        
        result = self.b.subscribeToEvent("ExistsNode", SubscribeBehaviour())
        self.assertEqual( result, ('ok', []) )
        #TODO: Check that the last published item is sent after subscription.
        
        self.b.eventmsg = None
        
        self.a.publishEvent('ExistsNode', Node(tag='foo'))
        
        import time
        time.sleep(3) #wait for the event
        #Check that the event is received in the callback
        self.assertNotEqual(self.b.eventmsg,None)
        
        n = self.b.eventmsg.T.event.T.items.T.item
        self.assertNotEqual(n.getTag("foo"),None)
        
        if not "a@"+host in n.getAttr("publisher"): self.fail("Wrong publisher")

        #TODO: Check that the new item published by 'a' is received too.
        
        self.b.unsubscribeFromEvent("ExistsNode")
        self.a.deleteEvent("ExistsNode")

    def testSubscribeNotAllowed(self):
        result = self.a.createEvent("ExistsNode")
        self.assertEqual(result, ('ok', ['ExistsNode']))
        
        result = self.b.subscribeToEvent("ExistsNode", jid="a@"+host)
        self.assertEqual(result, ('error', ['bad-request', 'invalid-jid']))
        
        self.a.deleteEvent("ExistsNode")
        
    def testUnsubscribeNotAllowed(self):
        result = self.a.createEvent("ExistsNode")
        self.assertEqual(result, ('ok', ['ExistsNode']))
        
        result = self.b.subscribeToEvent("ExistsNode")
        self.assertEqual( result, ('ok', []) )
                
        result = self.a.unsubscribeFromEvent('ExistsNode', jid='b@'+host)
        self.assertEqual(result, ('error', ['bad-request', 'invalid-jid']) )
        
        self.b.unsubscribeFromEvent("ExistsNode")
        self.a.deleteEvent("ExistsNode")

    def testResubscribeToEvent(self):
        result = self.a.createEvent("ExistsNode")
        self.assertEqual(result, ('ok', ['ExistsNode']))
        
        result = self.b.subscribeToEvent("ExistsNode")
        self.assertEqual( result, ('ok', []) )
        
        result = self.b.unsubscribeFromEvent("ExistsNode")
        self.assertEqual( result, ('ok', []))
        result = self.b.subscribeToEvent("ExistsNode")
        self.assertEqual( result, ('ok', [])) # OK
        #TODO: Check that the last published item is sent after subscription.
        
    def testNotEventBehaviour(self):
        
        class Behav(spade.Behaviour.Behaviour): pass
        self.a.deleteEvent("ExistsNode")
        self.b.deleteEvent("ExistsNode")
        self.a.createEvent("ExistsNode")
        result = self.b.subscribeToEvent("ExistsNode",Behav())
        self.assertEqual(result, ("error",["not-event-behaviour"]))
        
        

if __name__ == "__main__":
    #unittest.main()
    #sys.exit()

    suite = unittest.TestSuite()
    suite.addTest(PubSubTestCase('testCreateEvent'))
    result = unittest.TestResult()

    suite.run(result)
    for f in  result.failures:
        print f[0]
        print f[1]



