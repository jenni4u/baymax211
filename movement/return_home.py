import movement.line_follower as lf
    
def move_to_storage_room():
    """
    Moves robot from intersection to storage room.
    """
    lf.line_follower_distance(20, kp = -1.8)
    
    if lf.emergency_stop:
        return
    
    lf.move_forward(18)
    
    if lf.emergency_stop:
        return

def return_home(room: int):
    """
    Returns robot to storage room from specified room.  
    """

    if room == 4: 
        lf.line_follower_distance(2.0, -1.3, speed=-80, target=24)
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.smooth_turn()
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.move_forward(3)
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.smooth_turn()
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.turn_storage_room()
        
        if lf.emergency_stop:
            return
            
        move_to_storage_room()

    elif room == 2:
        # move forward to corner
        lf.line_follower_distance(2.0, -1.3, speed=-80, target=24)
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.smooth_turn()
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.move_forward(3)
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.move_forward(3)
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.smooth_turn()
        
        if lf.emergency_stop:
            return
            
        lf.line_follower()
        
        if lf.emergency_stop:
            return
            
        lf.turn_storage_room()
        
        if lf.emergency_stop:
            return
            
        move_to_storage_room()
        
        #TODO:play sucess sound, use Maria's function
        
    elif room == 3:
        # move forward to corner
        lf.line_follower()
        
        if lf.emergency_stop:
            return

        # turning at the top right corner
        lf.smooth_turn()
        
        if lf.emergency_stop:
            return

        #move forward to storage room intersection
        lf.line_follower()
        
        if lf.emergency_stop:
            return

        # turn towards storage room
        # assumes readjustments and alignment are included in the turning function
        lf.turn_storage_room()
        
        if lf.emergency_stop:
            return
        
        move_to_storage_room()
    elif room == 1:
        #move forward to storage room intersection
        lf.line_follower()
        
        if lf.emergency_stop:
            return

        lf.turn_storage_room()
        
        if lf.emergency_stop:
            return

        move_to_storage_room()

    



