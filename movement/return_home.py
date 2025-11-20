from utils.brick import Sound
import line_follower as lf

def success_sound(sound_file):
    """Play a sound to indicate successful return."""
    
    sound = Sound()
    sound.play_file(sound_file)


def return_home(room):
    """
    Returns robot to storage room from specified room.  
    """

    if room == 1:
        lf.line_follower(False)

        # turn towards storage room
        # assumes readjustments and alignment are included in the turning function
        lf.turn_right_on_self() 
        lf.line_follower() #TODO: measure distance and add
        
        

