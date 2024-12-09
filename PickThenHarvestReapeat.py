#Picking, harvesting, repeating
#Currently, it drives and harvests one green fruit, delivers it, and stops




# Library imports
from vex import *


#Defining the states
IDLE = 0
LINE_FOLLOWING = 1
SEARCHING = 2
APPROACHING = 3
HARVESTING = 4
DELIVERING = 5
NOTLINE_FOLLOWING = 6

current_state = IDLE

hasFruit = False

# Create a new object "brain_inertial" with the
# Inertial class.
brain_inertial = Inertial(Ports.PORT15)


#Motor and sensor initialization:
brain=Brain()
left_motor=Motor(Ports.PORT10, GearSetting.RATIO_18_1, True)
right_motor=Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
arm_motor = Motor(Ports.PORT15, GearSetting.RATIO_18_1, False)
basket_motor = Motor(Ports.PORT13)
controller = Controller()
brain_inertial = Inertial(Ports.PORT16)

LineFollowerR = Line(brain.three_wire_port.g)
LineFollowerL = Line(brain.three_wire_port.h)

sonars = Sonar(brain.three_wire_port.c)
sonarb = Sonar(brain.three_wire_port.e)

timer = 0
# # Start calibration.
brain_inertial.calibrate()
wait(3, SECONDS)


arm_motor.spin_to_position(300,DEGREES)

# Create a new object "controller" with the Controller class.
controller = Controller()

# Define a function button_pressed().
def button_pressed():
    # The Brain will print that the button was pressed on the
    # Brain's screen.
    brain.screen.print("button pressed")


# # Start calibration.
# brain_inertial.calibrate()
# wait(3, SECONDS)

Vision16__LIMEFRUIT = Signature (1, -6835, -6333, -6584, -3507, -2897, -3202, 2.9, 0)
Vision16__LEMONFRUIT = Signature (2, 1785, 4213, 2999, -4201, -3863, -4032, 3, 0)
Vision16__ORANGEFRUIT = Signature (3, 5021, 6599, 5810, -2193, -1827, -2010, 3, 0)
Vision16__GRAPEFRUIT = Signature (4, 4645, 7421, 6033, -2811, -2019, -2415, 3, 0)

Vision3 = Vision (Ports.PORT9, 50, Vision16__LEMONFRUIT)



#Button Press to initialize the robot
def handleButton():
    global current_state

    if(current_state == IDLE):
        print('IDLE -> LINE_FOLLOWING') ## Pro-tip: print out state _transitions_
        current_state = LINE_FOLLOWING
        drive()

    else: ## failsafe; go to IDLE from any other state when button is pressed
        print(' -> IDLE')
        current_state = IDLE
        left_motor.stop()
        right_motor.stop()

controller.buttonA.pressed(handleButton)




# current snapshot = camera.take picture
# previous snapshot = false

# if current snapshot true and previous snapshot false
#     then do it
#     previous snapshot = current snapshot



# Line following 
def drive():
    brain_inertial.reset_heading()

    global current_state
    global timer
    global missedDetections
    global hasFruit


    while current_state == LINE_FOLLOWING:
        print("LINEFOLLOWING")
        # print(timer)
    
        if LineFollowerL.reflectivity() > LineFollowerR.reflectivity():
            Delta = LineFollowerL.reflectivity() - LineFollowerR.reflectivity()
            LSpeed =  70 
            RSpeed =  70 + Delta
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
        if LineFollowerL.reflectivity() < LineFollowerR.reflectivity():
            Delta = LineFollowerR.reflectivity() - LineFollowerL.reflectivity()
            LSpeed =  70 + Delta
            RSpeed =  70
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
        if LineFollowerL.reflectivity() == LineFollowerR.reflectivity():
            LSpeed =  70
            RSpeed =  70 
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
            wait(1, MSEC)
        if sonars.distance(MM) < 450 and sonars.distance(MM) > 100 and sonars.distance(MM) > timer and hasFruit == False:  # TREE
            current_state = SEARCHING
            print('LINEFOLLOWING -> SEARCHING')
            missedDetections = 0
            turn()
        # if sonarb.distance(MM) < 50 and hasFruit == False:
        #     print('TURN ROW')
        #     # current_state = NOTLINE_FOLLOWING
        #     turnRow()
        print("SONAR DISTANCE", sonarb.distance(MM))
        print("HAS FRUIT=",  hasFruit)
        if sonarb.distance(MM) < 50 and hasFruit == True: # SEES BASKET
            current_state = DELIVERING
            deliver()
        timer -= 1
        wait(5, MSEC)

    while current_state == NOTLINE_FOLLOWING:
        print ('not line following')
        error = brain_inertial.heading() - 180
        if error >= 0:
            RSpeed = 70 
            LSpeed = 70 + abs (error * 0.1)
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
        if error < 0:
            RSpeed = 70 + abs (error * 0.1)
            LSpeed = 70
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
        else:
            LSpeed = 70
            RSpeed = 70
            left_motor.spin(FORWARD, LSpeed)
            right_motor.spin(FORWARD, RSpeed)
        if sonarb.distance(MM) < 90 and hasFruit == False:
            current_state = LINE_FOLLOWING
            turnRow()
        
        






def turnRow():
    global current_state
    global hasFruit
    print ("TURN ROW ACTIVATED")
    print("THE CURRENT STATE IS", current_state)

    if current_state == LINE_FOLLOWING:
        hasFruit = False
        print("HEADING =", brain_inertial.heading())
        print("HEADING =", brain_inertial.heading())
        left_motor.spin_for(FORWARD, 2880, DEGREES, wait=False)
        right_motor.spin_for(REVERSE, 2880, DEGREES)
        drive()
    print("THE CURRENT STATE IS", current_state)
    if current_state == DELIVERING:
        print("FRUIT HAS BEEN DELIVERED")
        hasFruit = False
        brain_inertial.reset_heading()
        print("HEADING =", brain_inertial.heading())
        print("HEADING =", brain_inertial.heading())
        left_motor.spin_for(FORWARD, 1450, DEGREES, 50, RPM, wait=False)
        right_motor.spin_for(REVERSE, 1450, DEGREES, 65, RPM)
        while brain_inertial.heading() <= 89:
            print("NO MORE DEAD")
            left_motor.spin(FORWARD, 40)
            right_motor.spin(REVERSE, 40)
        current_state = NOTLINE_FOLLOWING
        print("CURRENT STATE", current_state)
        drive()


            





def turn():

    if current_state == SEARCHING:
        left_motor.spin(FORWARD, 30)
        right_motor.spin(FORWARD, -50)

        ## start the timer for the camera
        cameraTimer.event(cameraTimerCallback, 50)


def deliver():
  
    global hasFruit
    global current_state
    print("CURRENT STATE", current_state)
    print("DELIVERING")
    if current_state == DELIVERING:
        hasFruit = False
        right_motor.stop()
        left_motor.stop()
        basket_motor.spin_for(FORWARD, 190, DEGREES, 40, RPM)
        wait(1, SECONDS)
        basket_motor.spin_for(REVERSE, 210, DEGREES, 40, RPM)
        print("CURRENT STATE", current_state)
        print("CURRENT STATE", current_state)
        turnRow()



# Searching for fruit NEW CODE
target_x = 175
K_x = 0.5
target_y = 148
K_y = 0.5
missedDetections = 0


cameraInterval = 50
cameraTimer = Timer()




def cameraTimerCallback():
    global current_state
    global missedDetections

    ## Here we use a checker-handler, where the checker checks if there is a new object detection.
    ## We don't use a "CheckForObjects()" function because take_snapshot() acts as the checker.
    ## It returns a non-empty list if there is a detection.
    objects = Vision3.take_snapshot(Vision16__LEMONFRUIT)
    # print(objects)
    if objects: handleObjectDetection()
    else: missedDetections = missedDetections + 1

    # restart the timer
    if(current_state == SEARCHING or current_state == APPROACHING):
        cameraTimer.event(cameraTimerCallback, 50)


def handleObjectDetection():
    global current_state
    global object_timer
    global missedDetections
# Need to make sure it goes for the object on the tree we want
    cx = Vision3.largest_object().centerX
    w = Vision3.largest_object().width
    h = Vision3.largest_object().height
    # print(cx)
    # print(cy)
    
    


    if current_state == SEARCHING and w > 20 and h > 20:
        goToFruit()
        print('SEARCHING -> APPROACHING') ## Pro-tip: print out state _transitions_


    ## Not elif, because we want the logic to cascade
    if current_state == APPROACHING:
        setArmHeight()




    ## reset the time out timer
    missedDetections = 0

def checkForLostObject():
    if(missedDetections > 100): 
        return True

    else: 
        return False
    
def setArmHeight():
    global hasFruit
    global current_state
    print("SetArmHeight")
    if current_state == APPROACHING:
        cy = Vision3.largest_object().centerY
        arm_error = target_y - cy
        arm_effort = K_y * arm_error
        arm_motor.spin(FORWARD, arm_effort)
        if abs (cy - target_y) <= 1:
            current_state = HARVESTING
            hasFruit = True
            touchedFruit()
            


def goToFruit():
    global current_state
    print("goToFruit")
    cx = Vision3.largest_object().centerX
    w = Vision3.largest_object().width
    error = cx - target_x
    turn_effort = K_x * error

    right_motor.spin(FORWARD, 30 - turn_effort)
    left_motor.spin(FORWARD, 30 + turn_effort)

        # arm_error = target_y - cy
        # arm_effort = K_y * arm_error
        # if abs (cy - target_y) > 1:
        #     arm_motor.spin(FORWARD, arm_effort)


## CHANGE
    if w >= 150 and abs (error) <= 1:
        current_state = APPROACHING
        left_motor.stop()
        right_motor.stop()
        handleObjectDetection()
    # if w >= 140 and not abs (error) <= 1:
    #     right_motor.stop()
    #     left_motor.spin(FORWARD, 30 + turn_effort)






def backOnLine():
    global current_state
    global timer
    global missedDetections

    missedDetections = 0
    print("backOnLine Running", current_state)
    if current_state == SEARCHING:
        print('LOOKING FOR LINE') ## Pro-tip: print out state _transitions_
        while brain_inertial.heading() > 3:
            left_motor.spin(FORWARD, -30)
            right_motor.spin(FORWARD, 30)
        # if brain_inertial.heading() < 10 or brain_inertial.heading() > 350:
         # left_motor.spin(FORWARD, 30)
        # right_motor.spin(FORWARD, 30)
        print('SEARCHING -> LINE_FOLLOWING') ## Pro-tip: print out state _transitions_
        timer = 1800
        current_state = LINE_FOLLOWING
        drive()
        # else:
            # print('LOOKING FOR LINE') ## Pro-tip: print out state _transitions_
            # left_motor.spin(FORWARD, -30)
            # right_motor.spin(FORWARD, 30)

def touchedFruit():
    global current_state
    if current_state == HARVESTING:

        left_motor.spin_for(FORWARD, 470, DEGREES, wait=False)
        right_motor.spin_for(FORWARD, 470, DEGREES)
        print("HARVESTING")
        arm_motor.spin_for(REVERSE, 180)
        arm_motor.stop()
        left_motor.spin_for(REVERSE, 940, DEGREES, wait=False)
        right_motor.spin_for(REVERSE, 940, DEGREES)
        current_state = SEARCHING
        backOnLine()

## Our main loop
while True:
    brain.screen.print_at("missed detections =", missedDetections, x=10, y=50)
    brain.screen.print_at("state =", current_state, x=10, y=80)
    brain.screen.print_at("reading =", brain_inertial.heading(), x=10, y=120)
    ## if enough cycles have passed without a detection, we've lost the object
    if(checkForLostObject()): backOnLine()





