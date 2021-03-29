import math

print(ship.angle)
if orientation < 5:
    ship.shoot()


vx = input_data['asteroids'][closest_asteroid]['velocity'][0]
vy = input_data['asteroids'][closest_asteroid]['velocity'][1]
vhyp = math.sqrt(vx ** 2 + xy ** 2)

bs = 800
shortest_distance

#Gives angle the asteroid is travelling 0-360
if vy > 0 and vx > 0:
    vectdang = math.degrees(math.atan(vy/vx))
elif vy <= 1 and vx > 0:
    vectdang = 90 - math.degrees(math.atan(vy/vx))
elif vy <= 1 and vx <= 0:
    vectdang = 180 + math.degrees(math.atan(vy/vx))
elif vy > 1 and vx <= 0:
    vectdang = 270 - math.degrees(math.atan(vy/vx))

castangle = 360 - normal_astangle  # clockwise asteroid angle

orientation_obj = ship.angle - s_rangle

# Gives angle the asteroid is traveling relative to the ship
if castangle < 90:
    perpangle = castangle-90
elif castangle < 180 and > 90:

elif castangle < 270 and > 180:

elif castangle < 360 and >270:

perpect = vhyp / math.radians(perpangle)

