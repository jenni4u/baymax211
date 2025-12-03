import line_follower as lf
import sounds_utils

emergency_stop = False
def move_to_storage_room():
    """
    Moves robot from intersection to storage room.
    """
    global emergency_stop
    lf.line_follower_distance(15, kp = -2)
    
    if emergency_stop:
        return
    
    lf.move_forward(21)
    
    if emergency_stop:
        return
    
    sounds_utils.play_wav("complete.wav")

def return_home(room: int):
    """
    Returns robot to storage room from specified room.  
    """
    global emergency_stop

    if room == 4: 
        lf.line_follower_distance(2.0, -1.3, speed=-80, target=24)
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.smooth_turn()
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.move_forward(3)
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.smooth_turn()
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.turn_storage_room()
        
        if emergency_stop:
            return
            
        move_to_storage_room()

    elif room == 2:
        # move forward to corner
        lf.line_follower_distance(2.0, -1.3, speed=-80, target=24)
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.smooth_turn()
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.move_forward(3)
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.move_forward(3)
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.smooth_turn()
        
        if emergency_stop:
            return
            
        lf.line_follower()
        
        if emergency_stop:
            return
            
        lf.turn_storage_room()
        
        if emergency_stop:
            return
            
        move_to_storage_room()
               
    elif room == 3:
        # move forward to corner
        lf.line_follower()
        
        if emergency_stop:
            return

        # turning at the top right corner
        lf.smooth_turn()
        
        if emergency_stop:
            return

        #move forward to storage room intersection
        lf.line_follower()
        
        if emergency_stop:
            return

        # turn towards storage room
        # assumes readjustments and alignment are included in the turning function
        lf.turn_storage_room()
        
        if emergency_stop:
            return
        
        move_to_storage_room()
    elif room == 1:
        #move forward to storage room intersection
        lf.line_follower()
        
        if emergency_stop:
            return

        lf.turn_storage_room()
        
        if emergency_stop:
            return

        move_to_storage_room()

    



