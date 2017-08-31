
Simple app to read pressure / temp from motino - paired with weewx scripts.

See http://docs.platformio.org/en/latest/quickstart.html for guide on how to build.

> platformio lib search SFE_BMP180
> platformio lib install <532>

> platformio lib search SI7021
> platformio lib install <1775>

> platformio lib update

> platformio run -v --target upload

Confirm device is working:
> platformio device monitor -b 115200
> <hit some keys>
