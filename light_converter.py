import math

def convert(log_scale_in: int, log_range = 255, lux_range = 3.47871075551):
    log_lux = log_range * log_scale_in / lux_range
    return math.pow(10, log_lux)

if __name__ == "__main__":
    print(convert(168))