import pytest
from client import MQTTClient
import mqtt_codec.packet as pkt
from io import BytesIO
import asyncio


@pytest.mark.asyncio
async def test_connect():
    c = MQTTClient()
    c.connect("id", True, 30)
    data1 = await c.bytes_to_send()

    connect = pkt.MqttConnect("id", True, 30)
    f = BytesIO()
    connect.encode(f)
    data2 = f.getvalue()

    assert data1 == data2, "Connect packet is wrong"

    conack = pkt.MqttConnack(False, pkt.ConnackResult.accepted)
    f = BytesIO()
    conack.encode(f)
    c.feed(f.getvalue())

    assert c.connected() == True


@pytest.mark.asyncio
async def test_subscribe():
    c = MQTTClient()
    c.connect("id", True, 30)
    await c.bytes_to_send()

    topics = (
        pkt.MqttTopic("mqtt-asyncio/sub1", 0),
        pkt.MqttTopic("mqtt-asyncio/sub2", 0),
    )
    sub_ev = c.subscribe(topics)
    data1 = await c.bytes_to_send()

    sub = pkt.MqttSubscribe(1, topics)
    f = BytesIO()
    sub.encode(f)
    data2 = f.getvalue()
    assert data1 == data2, "Subscribe packet is wrong"
    assert sub_ev.is_set() == False

    suback = pkt.MqttSuback(1, (pkt.SubscribeResult.qos0, pkt.SubscribeResult.qos0))
    f = BytesIO()
    suback.encode(f)
    c.feed(f.getvalue())

    assert sub_ev.is_set() == True


@pytest.mark.asyncio
async def test_publish_qos0():
    c = MQTTClient()
    c.connect("id", True, 30)
    await c.bytes_to_send()

    pub_ev = c.publish("test/topic", b"payload", 0, False)
    assert pub_ev == None
    data1 = await c.bytes_to_send()

    pub = pkt.MqttPublish(1, "test/topic", b"payload", False, 0, False)
    f = BytesIO()
    pub.encode(f)
    data2 = f.getvalue()

    assert data1 == data2


@pytest.mark.asyncio
async def test_publish_qos1():
    c = MQTTClient()
    c.connect("id", True, 30)
    await c.bytes_to_send()

    pub_ev = c.publish("test/topic", b"payload", 1, False)
    assert pub_ev != None
    assert isinstance(pub_ev, asyncio.Event)
    assert pub_ev.is_set() == False

    data1 = await c.bytes_to_send()
    pub = pkt.MqttPublish(1, "test/topic", b"payload", False, 1, False)
    f = BytesIO()
    pub.encode(f)
    data2 = f.getvalue()
    assert data1 == data2

    puback = pkt.MqttPuback(1)
    f = BytesIO()
    puback.encode(f)
    c.feed(f.getvalue())
    assert pub_ev.is_set()


@pytest.mark.asyncio
async def test_newmsg():
    c = MQTTClient()
    c.connect("id", True, 30)
    await c.bytes_to_send()

    pub = pkt.MqttPublish(1, "test/topic", b"payload", False, 0, False)
    f = BytesIO()
    pub.encode(f)
    c.feed(f.getvalue())

    msg = await c.get_messages()
    assert msg.topic == "test/topic"
    assert msg.payload == b"payload"
