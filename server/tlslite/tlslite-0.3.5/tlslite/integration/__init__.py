"""Classes for integrating TLS Lite with other packages."""

__all__ = ["AsyncStateMachine",
           "HTTPTLSConnection",
           "XMLRPCTransport",
           "TLSSocketServerMixIn",
           "TLSAsyncDispatcherMixIn",
           "TLSTwistedProtocolWrapper"]

try:
    import twisted
    del twisted
except ImportError:
   del __all__[__all__.index("TLSTwistedProtocolWrapper")]
