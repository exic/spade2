import os
import sys
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

import spade

class MyAgent(spade.Agent.Agent):
	class MyBehav(spade.Behaviour.OneShotBehaviour):
		def onStart(self):
			print "Starting behaviour . . ."

		def _process(self):
			print "I'm going to search for an agent"
			aad = spade.AMS.AmsAgentDescription()
			search = self.myAgent.searchAgent(aad)
			print search

		def onEnd(self):
			print "Ending behaviour . . ."

	def _setup(self):
		print "MyAgent starting . . ."
		b = self.MyBehav()
		self.addBehaviour(b, None)

if __name__ == "__main__":
	#a = MyAgent("agent@alien3.dsic.upv.es", "secret")
	a = MyAgent("agent@192.168.2.3", "secret")
	a.start()

