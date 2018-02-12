max = 40
states = 4 # leds + 1

step = (max / states) # float in python3

measure = 0
cur_state = 0

for i in range(states):
    if measure >= step * i:
        print("led high")
        # turn led (i)
        cur_state += 1
    else:
        print("led low")

print("state: {0}".format(cur_state))
print(step)