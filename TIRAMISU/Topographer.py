import math
import PyLidar3
import Poser
Sweeper = PyLidar3.YdLidarX4('COM6', 6000)
Sweeper.Connect()
SWEEPER_IS_ON = False
SWEEPER_GENERATOR = None
AVOID = 0
LANDMARK_MAP = [[[0]*3]*1000]*1000
PRESENCE_MAP = [[[0]*3]*1000]*1000
WALL_MAP = [[[-1]*3]*1000]*1000
WALL_SPLASH_MAP = [[[0]*3]*1000]*1000
EDGE_WEIGHT_MAP = [[[0]*3]*1000]*1000
VICTIM_X = 0
VICTIM_Y = 0

def sweeper_on(state):
    global SWEEPER_IS_ON
    global SWEEPER_GENERATOR
    if state:
        SWEEPER_GENERATOR = Sweeper.StartScanning()
        SWEEPER_IS_ON = True
    elif not state:
        Sweeper.StopScanning()
        SWEEPER_IS_ON = False


def plot_walls():
    lidardata = next(SWEEPER_GENERATOR)
    global AVOID
    AVOID = 0
    for angle in range(0, 360):
        if lidardata[angle] > 0:
            if 15 < angle < 45 and lidardata[angle]*0.1 < 14:
                AVOID = 1
            elif 315 < angle < 345 and lidardata[angle]*0.1 < 14:
                AVOID = -1
            angcos = math.cos(math.radians(angle+Poser.ROBOT_COMPASS))
            angsin = math.sin(math.radians(angle+Poser.ROBOT_COMPASS))
            for i in range(0, round(lidardata[angle]*0.1)):
                if WALL_MAP[round(Poser.ROBOT_POSITION_X+(i*angcos))][round(Poser.ROBOT_POSITION_Y+(i*angsin))][Poser.CURRENT_FLOOR] == (-1):
                    WALL_MAP[round(Poser.ROBOT_POSITION_X+(i*angcos))][round(Poser.ROBOT_POSITION_Y+(i*angsin))][Poser.CURRENT_FLOOR] = 0
                elif WALL_MAP[round(Poser.ROBOT_POSITION_X+(i*angcos))][round(Poser.ROBOT_POSITION_Y+(i*angsin))][Poser.CURRENT_FLOOR] == 1:
                    WALL_MAP[round(Poser.ROBOT_POSITION_X+(i*angcos))][round(Poser.ROBOT_POSITION_Y+(i*angsin))][Poser.CURRENT_FLOOR] = 0
                    for c in range(-15, 16):
                        for r in range(-15, 16):
                            if math.sqrt((c*c)+(r*r)) <= 9:
                                WALL_SPLASH_MAP[round(Poser.ROBOT_POSITION_X+(i*angcos)) + c][round(Poser.ROBOT_POSITION_Y+(i*angsin)) + r][Poser.CURRENT_FLOOR] -= 1
                            elif math.sqrt((c*c)+(r*r)) <= 15 and EDGE_WEIGHT_MAP[round(Poser.ROBOT_POSITION_X+(i*angcos)) + c][round(Poser.ROBOT_POSITION_Y+(i*angsin)) + r][Poser.CURRENT_FLOOR] >= 15-math.sqrt((c*c)+(r*r)):
                                EDGE_WEIGHT_MAP[round(Poser.ROBOT_POSITION_X+(i*angcos)) + c][round(Poser.ROBOT_POSITION_Y+(i*angsin)) + r][Poser.CURRENT_FLOOR] -= 15-math.sqrt((c*c)+(r*r))
            if WALL_MAP[round(Poser.ROBOT_POSITION_X+(lidardata[angle]*0.1*angcos))][round(Poser.ROBOT_POSITION_Y+(lidardata[angle]*0.1*angsin))][Poser.CURRENT_FLOOR] in (-1, 0):
                WALL_MAP[round(Poser.ROBOT_POSITION_X+(lidardata[angle]*0.1*angcos))][round(Poser.ROBOT_POSITION_Y+(lidardata[angle]*0.1*angsin))][Poser.CURRENT_FLOOR] = 1
                for c in range(-15, 16):
                    for r in range(-15, 16):
                        if math.sqrt((c*c)+(r*r)) <= 9:
                            WALL_SPLASH_MAP[round(Poser.ROBOT_POSITION_X+(lidardata[angle]*0.1*angcos)) + c][round(Poser.ROBOT_POSITION_Y+(lidardata[angle]*0.1*angsin)) + r][Poser.CURRENT_FLOOR] += 1
                        elif math.sqrt((c*c)+(r*r)) <= 15:
                            EDGE_WEIGHT_MAP[round(Poser.ROBOT_POSITION_X+(lidardata[angle]*0.1*angcos)) + c][round(Poser.ROBOT_POSITION_Y+(lidardata[angle]*0.1*angsin)) + r][Poser.CURRENT_FLOOR] += 15-math.sqrt((c*c)+(r*r))


def plot_presence():
    for c in range(-15, 16):
        for r in range(-10, 11):
            PRESENCE_MAP[Poser.ROBOT_POSITION_X + c*math.cos(math.radians(Poser.ROBOT_COMPASS))][Poser.ROBOT_POSITION_Y + r*math.sin(math.radians(Poser.ROBOT_COMPASS))][Poser.CURRENT_FLOOR] = 1


def plot_black_tile(floor):
    for c in range(30):
        for r in range(30):
            angle = math.radians(Poser.ROBOT_COMPASS) + math.atan((c-15)/(r+15))
            hipotenuse = math.sqrt(((c-15)*(c-15))+((r+15)*(r+15)))
            LANDMARK_MAP[round(Poser.ROBOT_POSITION_X + hipotenuse*math.cos(angle))][round(Poser.ROBOT_POSITION_Y + hipotenuse*math.sin(angle))][floor] = 99


def plot_victim(victim_type):
    global VICTIM_X
    global VICTIM_Y
    victim_found_in_radius = False
    wall_found_in_raytrace = False
    wall_dist = 15
    if victim_type > 0 and victim_type <= 7:
        angcos = math.cos(math.radians(Poser.ROBOT_COMPASS+270))
        angsin = math.sin(math.radians(Poser.ROBOT_COMPASS+270))
        for i in range(20):
            if WALL_MAP[round(Poser.ROBOT_POSITION_X + (i * angcos))][round(Poser.ROBOT_POSITION_Y + (i * angsin))][Poser.CURRENT_FLOOR] == 1:
                wall_found_in_raytrace = True
                wall_dist = i
                break
        for c in range(-15, 16):
            for r in range(-15, 16):
                if math.sqrt((c*c)+(r*r)) <= 15 and 0 < LANDMARK_MAP[round(Poser.ROBOT_POSITION_X+(wall_dist * angcos)+c)][round(Poser.ROBOT_POSITION_Y+(wall_dist * angsin)+r)][Poser.CURRENT_FLOOR] <= 14:
                    victim_found_in_radius = True
        if not victim_found_in_radius and wall_found_in_raytrace:
            LANDMARK_MAP[round(Poser.ROBOT_POSITION_X+(wall_dist * angcos))][round(Poser.ROBOT_POSITION_Y+(wall_dist * angsin))][Poser.CURRENT_FLOOR] = victim_type
            VICTIM_X = round(Poser.ROBOT_POSITION_X+(wall_dist * angcos))
            VICTIM_Y = round(Poser.ROBOT_POSITION_Y+(wall_dist * angsin))
            return True
        else:
            return False
    elif victim_type > 7:
        angcos = math.cos(math.radians(Poser.ROBOT_COMPASS+90))
        angsin = math.sin(math.radians(Poser.ROBOT_COMPASS+90))
        for i in range(20):
            if WALL_MAP[round(Poser.ROBOT_POSITION_X + (i * angcos))][round(Poser.ROBOT_POSITION_Y + (i * angsin))][Poser.CURRENT_FLOOR] == 1:
                wall_found_in_raytrace = True
                wall_dist = i
                break
        for c in range(-15, 16):
            for r in range(-15, 16):
                if math.sqrt((c*c)+(r*r)) <= 15 and 0 < LANDMARK_MAP[round(Poser.ROBOT_POSITION_X+(wall_dist * angcos)+c)][round(Poser.ROBOT_POSITION_Y+(wall_dist * angsin)+r)][Poser.CURRENT_FLOOR] <= 14:
                    victim_found_in_radius = True
        if not victim_found_in_radius and wall_found_in_raytrace:
            LANDMARK_MAP[round(Poser.ROBOT_POSITION_X+(wall_dist * angcos))][round(Poser.ROBOT_POSITION_Y+(wall_dist * angsin))][Poser.CURRENT_FLOOR] = victim_type
            VICTIM_X = round(Poser.ROBOT_POSITION_X+(wall_dist * angcos))
            VICTIM_Y = round(Poser.ROBOT_POSITION_Y+(wall_dist * angsin))
            return True
        else:
            return False
