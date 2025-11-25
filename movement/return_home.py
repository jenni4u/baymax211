import movement.line_follower as lf
    
def move_to_storage_room():
    """
    Moves robot from intersection to storage room.
    """
    lf.line_follower_distance(15, kp = -1.5)
    lf.move_forward(22)

def return_home(room: int):
    """
    Returns robot to storage room from specified room.  
    """

    if room == 4 or room == 2:
        # back up
        print("back up 1")
        lf.line_follower(False)
        print("back up 2")
        lf.move_forward(-3)
        print("back up 3")
        lf.line_follower(False)

        # turn towards storage room
        # assumes readjustments and alignment are included in the turning function
        lf.turn_storage_room() 

        move_to_storage_room()
        
        #TODO:play sucess sound, use Maria's function
    elif room == 3:
        # move forward to corner
        lf.line_follower()

        # turning at the top right corner
        lf.smooth_turn()

        #move forward to storage room intersection
        lf.line_follower()

        # turn towards storage room
        # assumes readjustments and alignment are included in the turning function
        lf.turn_storage_room()
        move_to_storage_room()
    elif room == 1:
        #move forward to storage room intersection
        lf.line_follower()

        lf.turn_storage_room()

        move_to_storage_room()




