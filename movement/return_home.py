
import line_follower as lf

def move_to_storage_room():
    """
    Moves robot from intersection to storage room.
    """
    #TODO: measure distances to put in the 2 functions
    lf.line_follower_distance(0)
    lf.move_forward(0)

def return_home(room: int):
    """
    Returns robot to storage room from specified room.  
    """

    if room == 1 or room == 3:
        # back up
        lf.line_follower(False)

        # turn towards storage room
        # assumes readjustments and alignment are included in the turning function
        lf.turn_storage_room() 

        move_to_storage_room()
        
        #TODO:play sucess sound, use Maria's function
    elif room == 2:
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
    elif room == 4:
        #move forward to storage room intersection
        lf.line_follower()

        lf.turn_storage_room()

        move_to_storage_room()




