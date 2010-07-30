import Behaviour
import xmlrpclib
import xmpp

import types

class RPCServerBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.result=None
        self.msg = self._receive(False)
        if self.msg != None:
            if self.msg.getType() == "set":
                
                self.myAgent.DEBUG("RPC request received: "+str(self.msg),'info',"rpc")
                
                mc = self.msg.getTag('query')
                params, name = xmlrpclib.loads("<?xml version='1.0'?>%s" % str(mc))
                name=name.lower()
                self.myAgent.DEBUG("Params processed: name="+name+" params="+str(params) + " in " + str(self.myAgent.RPC.keys()),"info","rpc")
                    
                if not self.myAgent.RPC.has_key(name):
                    self.myAgent.DEBUG("RPC: 404 method not found",'error',"rpc")
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(404, "method not found"))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
                    return
                    
                service,methodCall = self.myAgent.RPC[name]
                
                self.myAgent.DEBUG("service and method: "+ str(service) + " --> " + str(methodCall),"info","rpc")
                
                self.myAgent.DEBUG("Comparing service.getP(): "+ str(service.getP()) + " with params--> " + str(params),"info","rpc")
                ps = params[0].keys()
                for p in service.getP():
                    if str(p) not in ps:
                        self.myAgent.DEBUG("RPC: 500 missing precondition: "+str(p)+ " is not in "+str(params),'error',"rpc")
                        xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "missing precondition"))
                        reply = self.msg.buildReply("error")
                        reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                        reply.setType("result")
                        reply.setFrom(self.myAgent.JID)
                        self.myAgent.send(reply)
                        return
                
                try:
                    self.myAgent.DEBUG("Calling method "+str(methodCall)+" with params "+str(params),"info","rpc")
                    if params == (None,):
                        result = methodCall()
                    else:
                        args=""
                        for k,v in params[0].items():
                            args+=str(k)+"="+str(v)+","
                        args=args[:-1]
                        result = eval("methodCall("+args+")")
                except Exception,e:
                    self.myAgent.DEBUG("RPC: 500 method error: "+str(e),'error',"rpc")
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "method error: "+str(e)))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
                    return

                #Check postconditions
                try:
                    fail=False
                    outputs={}
                    if type(result) == types.DictType:
                        for q in service.getQ():
                            if q not in result.keys():
                                fail=True
                                break
                            else: outputs[q]=result[q]
                        params = (outputs,)
                    else:
                        self.myAgent.DEBUG("RPC method MUST return a dict.",'error',"rpc")
                        fail=True
                except:
                    fail=True
                if fail:
                    self.myAgent.DEBUG("RPC: 500 missing postcondition: "+str(service.getQ()),'error',"rpc")
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "missing postcondition"))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
                    return

                #Everything was ok. Return results
                xmlrpc_res = xmlrpclib.dumps( params , methodresponse=True,allow_none=True)
                reply = self.msg.buildReply("result")
                reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                self.myAgent.send(reply)
                self.myAgent.DEBUG("RPC: method succesfully served: "+ str(reply),'ok',"rpc")

        
        else:
            self.myAgent.DEBUG("RPCServerBehaviour returned with no message", "warn","rpc")
            
class RPCClientBehaviour(Behaviour.OneShotBehaviour):
    
    def __init__(self, service, inputs, num):
        Behaviour.OneShotBehaviour.__init__(self)
        self.service = service
        self.inputs = inputs
        self.num = num

    def _process(self):
        self.result=None
        
        #send IQ methodCall
        params = {}
        ps     = None
        ps = self.service.getP() #self.service.getDAD().getServices()[0].getProperty("P")
        for p in ps: #check all Preconditions are True
            if not p in self.inputs.keys():
                #if "askBelieve" in dir(self.myAgent):
                #    if not self.myAgent.askBelieve(p):
                self.myAgent.DEBUG("Precondition "+ str(p) + " is not satisfied. Can't call method "+self.service.getName(),'error',"rpc")
                self.result=False
                return
            else: params[p] = self.inputs[p]
        
        #params = tuple(ps)
        self.myAgent.DEBUG("Params processed: "+str(params),"info","rpc")
        
        #if agent is a BDIAgent check preconditions
        #if "askBelieve" in dir(self.myAgent):
        #    for p in params:
        #        if not self.myAgent.askBelieve(p):
        #            self.result=False
        #            self.myAgent.DEBUG("Precondition "+ str(p) + " is not satisfied. Can't call method "+self.service.getName(),'error',"rpc")
        #            return
            
        payload = xmlrpclib.dumps( (params,) , methodname=self.service.getName(),allow_none=True)
        self.myAgent.DEBUG("Marshalled "+payload,"info","rpc")
        payload_node = xmpp.simplexml.XML2Node(payload)
        to = xmpp.protocol.JID(self.service.getOwner().getName())
        iq = xmpp.protocol.Iq(typ='set',queryNS="jabber:iq:rpc",frm=self.myAgent.JID,to=to,attrs={'id':self.num})
        iq.setQueryPayload([payload_node])
        self.myAgent.DEBUG("Calling method with: "+str(iq),"info","rpc")
        self.myAgent.send(iq)
        self.myAgent.DEBUG(self.service.getName() + " method called. Waiting for response",'ok',"rpc")
        
        #receive IQ methodResponse
        self.msg = self._receive(True)
        if self.msg != None:
            self.myAgent.DEBUG("Response received for method "+self.service.getName()+":" +str(self.msg),'ok',"rpc")
            if self.msg.getType() == "result":
                try:
                    params, method = xmlrpclib.loads("<?xml version='1.0'?>%s" % self.msg)
                    self.DEBUG("Returned params "+str(params),'ok',"rpc")
                    self.result = params[0]
                    #if agent is a BDIAgent add result params as postconditions
                    #if "addBelieve" in dir(self.myAgent):
                    for k,q in self.result.items(): #[0]:
                            #self.myAgent.addBelieve(q)
                            self.myAgent.KB[k]=q
                    return self.result
                except Exception,e:
                    self.myAgent.DEBUG("Error executing RPC service: "+str(e),"error","rpc")
                    self.result = False
                    return False
            else:
                self.result = False
                return False
        else:
            self.result = False
            return False


