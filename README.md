
Simple app to read pressure / temp from motino - paired with weewx scripts.

# Building with platformio

See http://docs.platformio.org/en/latest/quickstart.html for guide on how to build.

```sh
> platformio lib search SFE_BMP180
> platformio lib install <532>

> platformio lib search SI7021
> platformio lib install <1775>

> platformio lib update

> platformio run --target upload
```

Confirm device is working:
```sh
> platformio device monitor -b 115200
> <hit some keys>
```
