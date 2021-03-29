from typing import Tuple, Dict, Any

from fuzzy_asteroids.fuzzy_controller import ControllerBase, SpaceShip


class FuzzyController(ControllerBase):
    """
    Class to be used by UC Fuzzy Challenge competitors to create a fuzzy logic controller
    for the Asteroid Smasher game.

    Note: Your fuzzy controller class can be called anything, but must inherit from the
    the ``ControllerBase`` class (imported above)

    Users must define the following:
    1. __init__()
    2. actions(self, ship: SpaceShip, input_data: Dict[str, Tuple])

    By defining these interfaces, this class will work correctly
    """

    def __init__(self):
        """
        Create your fuzzy logic controllers and other objects here
        """
        import skfuzzy.control as ctrl
        import numpy
        self.hi = 30
        self.wack = 0
        """
        Checking the asteroid angle relative to the ship
        """

        def r_angle(opposite, hypotenuse, abovebelow, leftright):
            import math
            if abovebelow > 0:
                angle = -1 * (math.degrees(math.asin(opposite / hypotenuse)))
            elif abovebelow < 0 and leftright < 0:
                angle = 180 + (math.degrees(math.asin(opposite / hypotenuse)))
            elif abovebelow < 0 and leftright > 0:
                angle = -180 + (math.degrees(math.asin(opposite / hypotenuse)))
            else:
                angle = 0
            return angle

        self.rangle = r_angle
        """
        Defensively shooting at an approaching asteroid, 
        I think for defensive shooting we could have it intentionally over shoot by turning too fast 
        as to simulate leading the shot
        """
        """
        Angle Normalizer if the difference is greater than 180 or less
        """

        def norm(angle):
            if angle > 0:
                new_angle = angle
            elif angle < 0:
                new_angle = 360 + angle
            else:
                new_angle = 0
            return new_angle

        self.norm = norm
        """
        Function That Tells You Whether Rotating Left or Right to the asteroid is faster
        0 is left, 1 is right
        use normalized angles
        """

        def leftrightcheck(shipangle, astangle):

            dif = shipangle - astangle

            if dif > 0:
                correct = 20
            else:
                correct = 20

            diff = dif
            absdiff = abs(diff)
            if absdiff < 180 and diff > 0:
                leftright = 1
            elif absdiff < 180 and diff < 0:
                leftright = 0
            elif absdiff > 180 and diff > 0:
                leftright = 0
            elif absdiff > 180 and diff < 0:
                leftright = 1
            else:
                leftright = 0
                print('problem in left right checker')
            return leftright

        self.leftright = leftrightcheck

        """
        Chaffe Clearing Rotation Controller
        """

        asteroid_num = ctrl.Antecedent(numpy.arange(0, 61, 1), 'asteroid_num')
        names = ['low', 'avg', 'high']
        asteroid_num.automf(names=names)
        TR = ctrl.Consequent(numpy.arange(-91, 271, 1), 'TR')
        TR.automf(names=names)
        tr_rule0 = ctrl.Rule(antecedent=(asteroid_num['low']), consequent=TR['low'], label='tr_rule_0')
        tr_rule1 = ctrl.Rule(antecedent=(asteroid_num['avg']), consequent=TR['avg'], label='tr_rule_1')
        tr_rule2 = ctrl.Rule(antecedent=(asteroid_num['high']), consequent=TR['high'], label='tr_rule_2')
        tr_system = ctrl.ControlSystem(rules=[tr_rule0, tr_rule1, tr_rule2])
        self.tr_sim = ctrl.ControlSystemSimulation(tr_system)

    def actions(self, ship: SpaceShip, input_data: Dict[str, Tuple]) -> None:

        """
        Compute control actions of the ship. Perform all command actions via the ``ship``
        argument. This class acts as an intermediary between the controller and the environment.

        The environment looks for this function when calculating control actions for the Ship sprite.

        :param ship: Object to use when controlling the SpaceShip
        :param input_data: Input data which describes the current state of the environment
        """
        import fuzzy_asteroids
        import skfuzzy.control as ctrl
        import math
        import numpy
        import random

        roe_zone = 300

        astnum = len(input_data['asteroids'])
        distance = numpy.zeros(astnum)
        shortest_distance = 1000
        closest_asteroid = 0
        total_velocity = abs((ship.velocity[0] ** 2 + ship.velocity[1] ** 2) ** 0.5)
        if total_velocity > 0:
            if ship.velocity[1] > 0:
                travel_angle = -1 * math.degrees(math.asin(ship.velocity[0] / total_velocity))
            elif ship.velocity[0] > 0:
                travel_angle = -180 + math.degrees(math.asin(ship.velocity[0] / total_velocity))
            elif ship.velocity[0] < 0:
                travel_angle = 180 + math.degrees(math.asin(ship.velocity[0] / total_velocity))
            else:
                travel_angle = 0

        sidefromcenter = 400 - ship.center_x
        above_center = 300 - ship.center_y
        distancefromcenter = ((ship.center_x - 400) ** 2 + (ship.center_y - 300) ** 2) ** 0.5
        if distancefromcenter > 0:
            anglefromcenter = self.rangle(sidefromcenter, distancefromcenter, above_center, sidefromcenter)
        else:
            anglefromcenter = 0
        """
        angle_from_center=self.rangle(sidefromcenter, distancefromcenter, above_center, sidefromcenter)
        """
        """Below it goes through the asteroids, 
        records their distance, 
        and sets the shortest distance and closest asteroid"""
        inrange_distance = numpy.zeros(astnum)
        inrange_asteroid = numpy.zeros(astnum)
        astrange = 0

        ab2 = numpy.zeros(100)
        lr2 = numpy.zeros(100)
        op2 = numpy.zeros(100)
        hyp2 = numpy.zeros(100)
        s_rangle_inrange = numpy.zeros(100)

        orientation2 = numpy.ones(100)*100

        for n in range(0, astnum):
            distance[n] = (((input_data['asteroids'][n]['position'][0]) - ship.center_x) ** 2 + (
                        (input_data['asteroids'][n]['position'][1]) - ship.center_y) ** 2) ** 0.5
            if distance[n] < shortest_distance:
                shortest_distance = distance[n]
                closest_asteroid = n

            #Lester's Multitasking
            elif distance[n] < roe_zone and input_data['asteroids'][n]['size'] < 3:
                inrange_distance[astrange] = distance[n]
                inrange_asteroid[astrange] = n
                astrange += 1

                # Lester's Orientation Calculator


                for m in range(1, astrange):
                    ab2[m] = input_data['asteroids'][closest_asteroid]['position'][1] - ship.center_y
                    lr2[m] = input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x
                    op2[m] = input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x
                    hyp2[m] = inrange_distance[m]
                    s_rangle_inrange[m] = self.rangle(op2[m], hyp2[m], ab2[m], lr2[m])

                    orientation2[m] = abs(ship.angle - s_rangle_inrange[m])



        abovebelow = input_data['asteroids'][closest_asteroid]['position'][1] - ship.center_y
        leftright = input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x
        opposite = (input_data['asteroids'][closest_asteroid]['position'][0] - ship.center_x)
        hypotenuse = shortest_distance
        s_rangle = self.rangle(opposite, hypotenuse, abovebelow, leftright)






        """
        s_rangle is the angle relative to the ship necessary for the ship to point at the closest asteroid
        """
        """ Positive if above, negative if below"""
        """ negative if left, positive if right"""
        print("---")

        orientation = abs(ship.angle - s_rangle)

        normal_shipangle = self.norm(ship.angle)
        normal_astangle = self.norm(s_rangle)
        normal_cangle = self.norm(anglefromcenter)
        diff = ship.angle - s_rangle
        leftright = self.leftright(normal_shipangle, normal_astangle)
        clast_size = input_data['asteroids'][closest_asteroid]['size']
        """
        This is the master if function in which it determines which behavior mode to fall into 
        """
        if ship.respawn_time_left > 0:
            if shortest_distance < 55 + (5 * clast_size):
                if orientation > 120:
                    ship.thrust = ship.thrust_range[1]
                elif orientation > 70 and orientation < 110 and shortest_distance < 45:
                    ship.thrust = 0
                    ship.turn_rate = 180
        elif total_velocity > 2.5:

            """
            Braking Manuever- For if the ship is going to fast. Probably best for when there's a lot of 
            asteroids and you do you don't want it to slignshot past on into another
            """

            t_orientation = abs(ship.angle - travel_angle)
            if travel_angle == 0:
                pass
            elif t_orientation > 60:
                print('braking engaged')
                print(t_orientation)
                ship.thrust = ship.thrust_range[1]
            elif t_orientation < 60:
                print('braking engaged')
                print(t_orientation)
                ship.thrust = ship.thrust_range[0]
            else:
                print('something wonky afoot')
                clast_size = input_data['asteroids'][closest_asteroid]['size']

        elif shortest_distance < 45 + (10 * clast_size):
            """Evasive Manuevers, I think we could expand this to considering the closest three 
                asteroids and fuzzily deciding which direction to flee in

                for cases where an asteroid is perpindicularly approaching it needs to be able to distinguish left and right anf
                behave accordingly """
            if orientation > 120:
                ship.thrust = ship.thrust_range[1]
            elif orientation > 70 and orientation < 110 and shortest_distance < 45:
                ship.thrust = 0
                ship.turn_rate = 180
            else:
                ship.thrust = ship.thrust_range[0]

        #Search and Destroy (Lester's)
        elif shortest_distance > 80 + (50 * clast_size):
            ship.thrust = ship.thrust_range[1]

        elif ship.center_x > 700 or ship.center_x < 100 or ship.center_y > 500 or ship.center_y < 100:
            turn = self.leftright(normal_shipangle, normal_cangle)
            center_orientation = abs(ship.angle - anglefromcenter)
            if center_orientation < 10:
                ship.thrust = ship.thrust_range[1]
            elif turn == 0:
                ship.turn_rate = 180
            else:
                ship.turn_rate = -180

        elif len(input_data['asteroids']) > 3:

            self.tr_sim.input['asteroid_num'] = len(input_data['asteroids'])
            self.tr_sim.compute()
            ship.turn_rate = self.tr_sim.output['TR']
            """We'll need to use orientation to teach it to break since velocity can be measured using r_angle"""

        else:
            ship.turn_rate = 40



        if leftright == 0 and orientation > 5:
            ship.turn_rate = 180
        elif leftright == 0 and orientation <= 5:
            ship.turn_rate = 90
        elif leftright == 1 and orientation > 5:
            ship.turn_rate = -180
        else:
            ship.turn_rate = -90

        print()
        self.wack += 6000

        for l in range(0, len(orientation2)):
            #print(orientation2)
            if orientation < 2 or orientation2[l] < 4:
            #if orientation2[l] < 100:
                #print(orientation2[l])
                #if orientation2[l] < 10:
                    #print('TRICK SHOT!')
                if self.wack > hypotenuse**2:
                    self.wack = 0
                    ship.shoot()
