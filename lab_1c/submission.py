from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream# as MockTransport
from playground.network.testing import MockTransportToProtocol
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BOOL, BUFFER
import io, asyncio
from playground.network.protocols.packets.vsocket_packets import VNICSocketOpenPacket, VNICSocketOpenResponsePacket, \
    PacketType
from playground.network.protocols.packets.switching_packets import WirePacket


class ConnectionRequest(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.student_x.ConnectionRequest"
    DEFINITION_VERSION = "1.0"
    FIELDS = []
# This is the class used in the first step of my protocol: client send ConnectionRequest() to server

class VerifyingInfo(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.student_x.VerifyingInfo"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("ID", UINT32),
        ("IfPermit", BOOL)
    ]
# This is the class used in the second step of my protocol:server send VerifyingInfo(ID, IfPermit) to client

class ConnectionInfo(PacketType):
    DEFINITION_IDENTIFIER = "lab1b.student_x.ConnectionInfo"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("ID", UINT32),
        ("Address", STRING)
    ]
# This is the class used in the third step of my protocol:client send ConnectionInfo(ID, address) to server

class MyClientProtocol(asyncio.Protocol):
    state = 0
    def __init__(self):
        self._deserializer = PacketType.Deserializer()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
       # pktCR = ConnectionRequest()
       # transport.write(pktCR.__serialize__())
        print("Client made success")
        #self._deserializer = PacketType.Deserializer()

    def data_received(self, data):
        self._deserializer.update(data)
        print("Client receive data")
        self.state = 1
        for pkt in self._deserializer.nextPackets():
            #print(pkt)
            if pkt == None:
                print("Error.The packet is empty.")
                self.transport.close
            else:
                if isinstance(pkt, VerifyingInfo):
                    if self. state == 1:
                        print("The state of the client now is %d" % self.state)
                        print("The packet is VerifyingInfo")
                    #if pkt.DEFINITION_IDENTIFIER == "lab1b.student_x.VerifyingInfo":
                        if pkt.IfPermit == True:
                            pktCI = ConnectionInfo()
                            pktCI.ID = pkt.ID
                            pktCI.Address = "1.1.1.1"
                            self.state = 2
                            print("The client is sending ConnectionInfo to the server")
                            self.transport.write(pktCI.__serialize__())
                            print("The client finish sending ConnectionInfo to the server")
                        else:
                            print("Don't get permission!Connection fail.")
                            self.transport.close()
                    else:
                        print("The state of the server now is ERROR")
                        self.transport.close
                else:
                    print("Error.The type of the received packet is wrong.")
                    self.transport.close()


    def connection_lost(self, exc):
        self.transport = None
        print("The connection is stopped(Client).")

    def send(self, packet):
        self.transport.write(packet.__serialize__())


class MyServerProtocol(asyncio.Protocol):
    ConnectionID = 0
    state = 0
    def __init__(self):
        self.transport = None
        self._deserializer = PacketType.Deserializer()

    def connection_made(self, transport):
        self.transport = transport
        self._deserializer = PacketType.Deserializer()
        print("Server made success")

    def data_received(self, data):
        self._deserializer.update(data)
        print("Server receive data")
        for pkt in self._deserializer.nextPackets():
            #print(pkt)
            if pkt == None:
                print("Error.The packet is empty.")
                self.transport.close()
            else:
                if isinstance(pkt, ConnectionRequest):
                    self.state = 0
                    print("The state of the server now is %d" % self.state)
                    print("The packet is ConnectionRequest")
                    #if pkt.DEFINITION_IDENTIFIER == "lab1b.student_x.ConnectionRequest":
                    pktVI = VerifyingInfo()
                    self.ConnectionID = self.ConnectionID + 1
                    pktVI.ID = self.ConnectionID
                    pktVI.IfPermit = True
                    self.state = 1
                    print("The server is sending the VerifyingInfo to the client")
                    self.transport.write(pktVI.__serialize__())
                    print("The server finish sending the VerifyingInfo to the client")

                elif isinstance(pkt,ConnectionInfo):
                    self.state = 2
                    print("The state of the server now is %d" % self.state)
                    print("The packet is ConnectionInfo")
                    #pkt.DEFINITION_IDENTIFIER == "lab1b.student_x.ConnectionInfo":
                    print("Connection success!")
                    print("The ID of the Client is %d" % pkt.ID)
                    print("The Address of the Cilent is %s" % pkt.Address)
                    self.state = 3
                    print("The state of the server now is %d" % self.state)
                    #self.transport.close()
                else:
                    print("Error.The type of the received packet is wrong.")
                    self.transport.close()


    def connection_lost(self, exc):
        self.transport = None
        print("The connection is stopped(Server)")

def basicUnitTest():
    asyncio.set_event_loop(TestLoopEx())
    client=MyClientProtocol()
    server=MyServerProtocol()
    transportToServer=MockTransportToProtocol(myProtocol = client)
    transportToClient=MockTransportToProtocol(myProtocol = server)
    transportToServer.setRemoteTransport(transportToClient)
    transportToClient.setRemoteTransport(transportToServer)
    server.connection_made(transportToClient)
    client.connection_made(transportToServer)
    pktCR = ConnectionRequest()
    #pktCR2 = ConnectionRequest()
    #pktCR3 = ConnectionRequest()
    print("Start test. The packet is sent.")
    client.send(pktCR)
    #client.send(pktCR2)
    #client.send(pktCR3)
    print("Test End")

if __name__=="__main__":
    basicUnitTest()
    print("Test Success.")


