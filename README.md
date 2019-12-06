# MARS 2019

Codebase for the MARS club @ UVA

## Setup Manual Control

Launch the server script on Jetson nano

```bash
python -m mars_2019.jetson.server
```

Then launch the gamepad state interpreter

```bash
python -m mars_2019.laptop.gamepad_encoder
```