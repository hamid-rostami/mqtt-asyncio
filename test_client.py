import pytest
from client import MqttClient
import mqtt_codec.packet as pkt
from io import BytesIO


@pytest.mark.asyncio
async def test_connect():
    c = MqttClient()
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
    c = MqttClient()
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
