from distutils.core import setup

setup(
    name="mqtt_asyncio",
    packages=["mqtt_asyncio"],
    version="0.1",
    description="An implementation of MQTT for asyncio",
    author="Hamid Rostami",
    author_email="hamid.r1988@gmail.com",
    url="https://github.com/hamid-rostami/mqtt-asyncio",
    download_url="https://github.com/hamid-rostami/mqtt-asyncio/archive/refs/tags/0.1.tar.gz",
    keywords=["MQTT", "asyncio", "sans-io"],
    install_requires=["mqtt-codec"],
    classifiers=[],
)
