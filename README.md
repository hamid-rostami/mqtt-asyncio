# Introduction
A implementation of MQTT for asyncio. This library is designed by sans-io concept.
Means that it doesn'r perform any network operation. For example when you create
a MqttClient instance, you can use its API to connect, subscribe and so on. Then
it gives you a stream of bytes to write on network socket. Also all the bytes which
you receive from netowrk should be given to the object.

Maybe you wonder why I implement it in this way. If yes, I suggest you to follow
this link and read about Sans-IO:

https://sans-io.readthedocs.io

This library is dependent to a great library which is sans-io implementation of
MQTT protocol: `mqtt-codec`

https://mqtt-codec.readthedocs.io/en/latest/index.html

# Tests
To learn about API, take a look at `example.py`. I try to cover the code with
test units, so you can run the tests using this command:

```
python3 -m pytest -v
```

# Contribution

The code is under development, so maybe the API will be changed and of course
I look forward to your help and suggestions. Feel free to send pull requests and
open issues.