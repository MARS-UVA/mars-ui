# Action Parameter Notes

## Required parameters for all actions:
- `name`: the name of the action
- `update_delay`: how frequently the Jetson executes and check completion of the action

## Action-specific parameters:
- Raise/lower bin
    - `speed`: how fast the actuators move, between 0 (min) and 100 (max). Probably should be in the range 20-100. 
- Raise/lower ladder
    - `speed`: how fast the actuators move, between 0 (min) and 100 (max). 