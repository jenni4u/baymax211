import line_follower as lf
import return_home as rh

def test(t):
    lf.line_follower()
    print("intersection")
    lf.move_forward(3)
    lf.line_follower_distance(17.5, -1.5)
    print("return home")
    rh.return_home(t)
        
test(2)
# print("line follower")
# lf.line_follower()
# print("smooth turn")
# lf.smooth_turn()
# print("line follower distance 10")
# lf.line_follower_distance(10)