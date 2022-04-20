"""
Byte order that the hero expects:
- drive front left
- drive front right
- drive back left
- drive back right
- bucket ladder lifters
- bucket extender
- bucket chain driver
- deposit bin lifters
- conveyor driver

This function notably duplicates some of the motor values so that the resulting packet has 1 value for every single motor
"""
def encode_values(left_side_motors, right_side_motors, bucket_ladder_angle, bucket_ladder_extension, bucket_ladder_chain, deposit_bin_angle, conveyor):
    return bytes([
        left_side_motors, right_side_motors, left_side_motors, right_side_motors, 
        bucket_ladder_angle, bucket_ladder_extension, bucket_ladder_chain, deposit_bin_angle, conveyor
    ])
