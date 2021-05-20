import mqtt_codec.packet as pkt
import mqtt_codec.io

from io import BytesIO
import asyncio
import time


class _WaitingPacket:
    class Item:
        def __init__(self, packet_id):
            self.packet_id = packet_id
            self.event = asyncio.Event()
            self._ts = time.time()

    def __init__(self):
        self._items = []

    def add(self, packet_id):
        item = _WaitingPacket.Item(packet_id)
        self._items.append(item)
        return item.event

    def release(self, packet_id):
        for i in self._items:
            if i.packet_id == packet_id:
                i.event.set()
                self._items.remove(i)
                break


class MQTTClient:
    def __init__(self):
        self._keepalive = 30
        self._hdr = None
        self._packetid = 0

        # Queue of byte streams to send
        self._sendq = asyncio.Queue()

        # Queue of messages that have received
        self._new_msgq = asyncio.Queue()

        # Time of the last pingresp packet, used in keepalive process
        self._last_pong = time.time()

        # pingcnt increase when a ping packet is sent and will be decrease
        # when pingresp packet has recieved. It's for trakcing how many
        # ping packets are lost
        self._pingcnt = 0

        # Unacknowledge subscribes
        self._unack_subs = _WaitingPacket()

        # Unacknowledge unsubscribes
        self._unack_unsubs = _WaitingPacket()

        # Unacknowledge publishes
        self._unack_pubs = _WaitingPacket()

        # Connect event and result
        self._connack_ev = asyncio.Event()
        self._connect_result = None

        # Inner functions to call when specific packet has received
        self._callmap = {
            pkt.MqttControlPacketType.connack: self._connack,
            pkt.MqttControlPacketType.suback: self._suback,
            pkt.MqttControlPacketType.unsuback: self._unsuback,
            pkt.MqttControlPacketType.puback: self._puback,
            pkt.MqttControlPacketType.publish: self._publish,
            pkt.MqttControlPacketType.pingresp: self._pingresp,
        }

    def _get_packetid(self):
        if self._packetid < 2 ** 16:
            self._packetid += 1
        else:
            self._packetid = 1
        return self._packetid

    def _connack(self, hdr, f):
        num, connack = pkt.MqttConnack.decode_body(hdr, f)
        self._connect_result = connack.return_code
        self._connack_ev.set()
        print("MQTT Connected")

    def _suback(self, hdr, f):
        num, suback = pkt.MqttSuback.decode_body(hdr, f)
        self._unack_subs.release(suback.packet_id)

    def _unsuback(self, hdr, f):
        num, unsuback = pkt.MqttUnsuback.decode_body(hdr, f)
        self._unack_unsubs.release(unsuback.packet_id)

    def _puback(self, hdr, f):
        num, puback = pkt.MqttPuback.decode_body(hdr, f)
        self._unack_pubs.release(puback.packet_id)

    def _publish(self, hdr, f):
        num, pub = pkt.MqttPublish.decode_body(hdr, f)
        self._new_msgq.put_nowait(pub)

    def _pingresp(self, hdr, f):
        num, pub = pkt.MqttPingresp.decode_body(hdr, f)
        self._last_pong = time.time()
        self._pingcnt -= 1

    async def bytes_to_send(self):
        i = await self._sendq.get()
        return i.getvalue()

    def feed(self, data):
        # TODO
        f = BytesIO(data)
        num, self._hdr = pkt.MqttFixedHeader.decode(f)

        try:
            self._callmap[self._hdr.packet_type](self._hdr, f)
        except KeyError:
            raise NotImplementedError(self._hdr.packet_type)

    def _send(self, packet):
        i = BytesIO()
        packet.encode(i)
        self._sendq.put_nowait(i)

    async def wait_for_connect(self):
        await self._connack_ev.wait()
        return self._connect_result

    def connect(self, *args, **kwargs):
        connect = pkt.MqttConnect(*args, **kwargs)
        self._keepalive = args[2]
        self._send(connect)

    def subscribe(self, topics):
        packid = self._get_packetid()
        sub = pkt.MqttSubscribe(packid, topics)
        self._send(sub)
        return self._unack_subs.add(packid)

    def unsubscribe(self, topics):
        packid = self._get_packetid()
        unsub = pkt.MqttUnsubscribe(packid, topics)
        self._send(unsub)
        return self._unack_unsubs.add(packid)

    def publish(self, topic, payload, qos, retain):
        assert qos < 2, "QoS2 is not supported yet"
        packid = self._get_packetid()
        pub = pkt.MqttPublish(packid, topic, payload, False, qos, retain)
        self._send(pub)
        if qos == 0:
            return None
        else:
            return self._unack_pubs.add(packid)

    async def get_messages(self):
        return await self._new_msgq.get()

    def connected(self):
        if self._connect_result != pkt.ConnackResult.accepted:
            return False
        return True

    async def keepalive_task(self):
        # Decrese keepalive time by 2 seconds to make sure ping packet
        # will be arrived in appropriate time
        if self._keepalive > 2:
            timeout = self._keepalive - 2
        else:
            timeout = 5

        res = await self.wait_for_connect()

        while self.connected():
            await asyncio.sleep(1)
            if self._pingcnt > 5:
                self._connect_result = None
            diff = time.time() - self._last_pong
            if diff < timeout:
                continue
            ping = pkt.MqttPingreq()
            self._pingcnt += 1
            self._send(ping)
