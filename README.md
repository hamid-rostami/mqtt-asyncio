# Introduction

This is an implementation of MQTT for asyncio. This library is designed by
having sans-io concept in mind. Means that it doesn't perform any network
operations. For example when you create a MqttClient instance, you can use
its API to connect, subscribe and so on. Then it gives you a stream of bytes
to write to network socket. Also all the bytes which you receive from network
should be given to the object for further processing.

Maybe you wonder why I implemented it in this way. If yes, I suggest you to follow
this link and read about Sans-I/O:

https://sans-io.readthedocs.io

This library is dependent to a great library which is a sans-io implementation of
MQTT protocol: `mqtt-codec`

https://mqtt-codec.readthedocs.io/en/latest/index.html

# How to install

Can be installed using `pip` command:

```
pip install mqtt-asyncio
```

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