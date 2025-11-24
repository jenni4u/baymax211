import line_follower as lf
import return_home as rh

def test(t):
    lf.line_follower()
    print("intersection")
    lf.line_follower_distance(17.5)
    print("return home")
    rh.return_home(t)
        
test(3)
