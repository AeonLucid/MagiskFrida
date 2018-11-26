# MagiskFrida [![AppVeyor](https://img.shields.io/appveyor/ci/AeonLucid/MagiskFrida/master.svg?maxAge=60)](https://ci.appveyor.com/project/AeonLucid/MagiskFrida)

## Description

Runs frida-server on boot as root with magisk.
For more information on frida, see https://www.frida.re/docs/android/.

## Instructions

Flash the zip for your platform using TWRP or Magisk Manager.

You can either grab the zip file from the [release page](https://github.com/AeonLucid/MagiskFrida/releases) or build it yourself.

In order to build it:

```
git clone https://github.com/AeonLucid/MagiskFrida
cd MagiskFrida
pip3 install -r requirements.txt
python3 build.py
```

Two zip files will be generated in the same folder, grab the right architecture.
