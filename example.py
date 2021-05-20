import asyncio
import mqtt_codec.packet as pkt
from client import MqttClient
from uuid import uuid4


async def main():
    print("Client started")
    reader, writer = await asyncio.open_connection("localhost", 1883)
    c = MqttClient()
    clientid = "mqttsansio-" + uuid4().hex
    c.connect(clientid, True, 30)

    async def reader_task():
        while True:
            data = await reader.read(1024)
            if len(data) == 0:
                print("Connection lost")
                break
            c.feed(data)

    async def writer_task():
        while True:
            data = await c.bytes_to_send()
            writer.write(data)
            await writer.drain()

    async def publisher():
        await c.wait_for_connect()
        while True:
            ev = c.publish("mqtt-asyncio/pub", b"hi", qos=1, retain=False)
            await ev.wait()
            print("Publish OK")
            await asyncio.sleep(3)

    async def subscriber():
        topics = (
            pkt.MqttTopic("mqtt-asyncio/sub1", 0),
            pkt.MqttTopic("mqtt-asyncio/sub2", 0),
        )
        res = await c.wait_for_connect()
        sub_ev = c.subscribe(topics)
        await sub_ev.wait()
        print("Subscribed")

        while True:
            msg = await c.get_messages()
            print(msg.topic, msg.payload)

    t1 = asyncio.create_task(reader_task())
    t2 = asyncio.create_task(writer_task())
    t3 = asyncio.create_task(c.keepalive_task())
    t4 = asyncio.create_task(publisher())
    t5 = asyncio.create_task(subscriber())

    await t1
    t2.cancel()
    t3.cancel()
    t4.cancel()
    t5.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bye")
