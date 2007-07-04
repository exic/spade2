#! /usr/bin/python

from spade import *
from spade.ACLMessage import *
import os
import time
import sys
import pdb
from string import *
from threading import Lock

class emissor(Agent.Agent):
    nagents=0
    lock=Lock()

    def incrementa_agents(self):
        emissor.lock.acquire()
        emissor.nagents=emissor.nagents+1
        emissor.lock.release()
        
    def decrementa_agents(self):
        emissor.lock.acquire()
        emissor.nagents=emissor.nagents-1
        emissor.lock.release()

    class BehaviourDefecte(Behaviour.Behaviour):
                
        def _process(self):
            #agafar temps
            t1=time.time()

            #print "Vaig a enviar un missatge"
	    self.myAgent.msg.setContent("Missatge " +str( self.myAgent.nenviats))
            self.myAgent.send(self.myAgent.msg)
           
	    #print "Estic asperant ..." 
            recv = self._receive(True)
            #print "He rebut la contestacio"
            #agafar temps
            t2=time.time()

            if self.myAgent.nenviats < self.myAgent.nmsg:
                self.myAgent.mitjana = self.myAgent.mitjana + t2 - t1
            self.myAgent.nenviats=self.myAgent.nenviats+1
            #print "Missatge enviat"
            #print "Missatge",self.myAgent.nenviats
	    #time.sleep(1)

        def done(self): 
            if self.myAgent.nenviats == self.myAgent.nmsg + 5: return True
            else: return False

	def onStart(self):
		pass
		#print "EMISOR BEHAV: "+ str(self.getQueue())

        def onEnd(self):
            #posar estadistiques i si es l'ultim killall
            #print "Mitjana RTT",self.myAgent.mitjana/self.myAgent.nmsg
            self.rtt = "Mitjana RTT " + str(self.myAgent.mitjana / self.myAgent.nmsg) + "\n"
	    self.nom_fitxer = os.sep + "tmp" + os.sep + str(self.myAgent.getName()) + ".log"
	    f = open(self.nom_fitxer, "w")
	    f.write(str(self.myAgent.getName()))
	    f.write(" ")
	    f.write(self.rtt)
	    f.close()
            self.myAgent.decrementa_agents()
            #pdb.set_trace()
            #if emissor.nagents == 0:
            #    os.system("killall -9 /usr/bin/python;killall -9 /usr/local/bin/jabberd;rm -f jabber.pid")#canviar!!


            

    def __init__(self,jid,passw,nagent,ntotal,tmsg,nmsg,multiemissor,debug=[]):
        Agent.Agent.__init__(self,jid,passw, debug=debug)
        self.ntotal = ntotal
        self.tmsg = tmsg
        self.nmsg = nmsg
        self.nagent = nagent
        self.multi = multiemissor


           

    def _setup(self):
	#print "EMISOR: "+ str(self.getQueue())
        self.mitjana = 0
        self.nenviats = 0
        self.msg = ACLMessage()
        self.msg.setPerformative("inform")
        if self.multi:
            #self.msg.addReceiver(AID.aid("receptor0@"+host,self.myAgent.getAID().getAdresses()[0]["xmpp://acc."+host]))
            self.msg.addReceiver(AID.aid("receptor0@"+host,["xmpp://acc."+host]))
        else:
            self.msg.addReceiver(AID.aid("receptor%i@"%(self.nagent)+host,["xmpp://acc."+host]))
	#self.msg.addReceiver(AID.aid("ping@"+host,["xmpp://acc."+host]))

        string = ""
        for i in range(self.tmsg):
            string = string + "a"
        self.msg.setContent(string)


        #esperem a que estiguen tots els agents 
        self.incrementa_agents()
        while emissor.nagents != self.ntotal:
            time.sleep(5)

        if self.nagent==4:
            time.sleep(20)

        db = self.BehaviourDefecte()
        self.setDefaultBehaviour(db)

        

if __name__ == "__main__":
    host = os.getenv("HOSTNAME")
    if host == None:
        host = split(os.getenv("SESSION_MANAGER"),"/")[1][:-1]
        if host == None:
            host = "sandoval.dsic.upv.es"
            print "No s'ha pogut obtindre nom de host, utilitzant: "+host+" per defecte"

    emissors = {}
    nagents = atoi(sys.argv[1])
    tmsg = atoi(sys.argv[2])
    nmsg = atoi(sys.argv[3])
    multiemissor = 0
        
    if len(sys.argv) == 5 and sys.argv[4] == "m":
        multiemissor = 1
        
        
    for i in range(nagents-1):
        agent="emissor%i@"%(i)+host
        emissors[i] = emissor(agent,"secret",i,nagents,tmsg,nmsg,multiemissor)
        print "agent "+agent+" registrant-se!!"
        emissors[i].start()
        #time.sleep(20)

    start_time = time.time() 
    agent="emissor%i@"%(nagents-1)+host
    ultim = emissor(agent,"secret",nagents-1,nagents,tmsg,nmsg,multiemissor)
    print "agent "+agent+" registrant-se!!"
    #ultim.start_and_wait()
    ultim.start()
    while emissor.nagents != 0:
		#elapsed_time = time.time() - start_time
		#print "Tiempo transcurrido: " + str(elapsed_time)
		time.sleep(0.1)
    elapsed_time = time.time() - start_time
    print "Tiempo transcurrido: " + str(elapsed_time)
    print "Enviados en total " + str(nagents*nmsg*2) + " mensajes de " + str(tmsg) + "bytes"



# TODO:parametritzar el host del acc i del desti
