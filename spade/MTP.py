# encoding: utf-8
from spade import SpadeConfigParser
from spade import XMLCodec
from spade import ACLParser
from xmpp import *

class MTP:

	def __init__(self, name, config, acc):

		#parser = SpadeConfigParser.ConfifParser()
		#self.config = parser.parse(CONFIGFILE)

		self.name = name
		self.config = config
		self.acc = acc

		self.protocol = self.config.acc.mtp[name].protocol
		#self.instance = self.config.acc.mtp[name].instance

		self.setup()

	def setup(self):
		raise NotImplemented

	# Envelope = Envelope Class
	# Payload = raw text
	def send(self, envelope, payload):
		raise NotImplemented

	def stop(self):
	    #raise NotImplemented
	    pass


	def dispatch(self, envelope, payload):
		"""
		xc = XMLCodec.XMLCodec()
		envxml = xc.encodeXML(envelope)

		xenv = protocol.Node('jabber:x:fipa x')
		xenv['content-type']='fipa.mts.env.rep.xml.std'
		xenv.addData(envxml)
		"""
		#print "DISPATCH PAYLOAD"
		#print str(payload)
		p = ACLParser.ACLParser()
		msg = p.parse(payload)
		#print "###MTP MESSAGE PARSED"
		#print msg

		# Try to send message through XMPP
		# If no xmpp address is found, try to come uo with one
		try:
			for recv in msg.getReceivers():
				jabber_id = ""
				for addr in recv.getAddresses():
					if "xmpp" in addr:
						jabber_id = addr
						break
				if not jabber_id:
					jabber_id = "xmpp://"+str(recv.getName())
					# Figuring out the XMPP address
					recv.addAddress(jabber_id)

			self.acc.send(msg, "jabber")

		except:
			self.acc.send(msg, "jabber")

		"""
		for to in envelope.getTo():

			stanza = protocol.Message(to.getName(),payload, xmlns="")
			stanza.addChild(node=xenv)

			#s=None
			#s = self.acc._router._owner.getsession(to.getName())
			self.acc.send(stanza)
			print ">>>MTP: sent message to ", str(to)
			#print ">>>MTP: found session " + str(s) + "for " + str(to.getName())
			#if s:
			#	s.enqueue(stanza)
			#	s.push_queue()
		"""



PROTOCOL = None  #This must be overriden
INSTANCE = None  #This must be overriden

