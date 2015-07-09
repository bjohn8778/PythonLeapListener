import Leap,FrameListener
#from numpy import *

if __name__ == '__main__':
    
    #test Leap
    controller = Leap.Controller()
    
    print 'LEAP connected is ' + controller.is_connected.__str__()
    
    #we want tracking data in background
    #other flags are for image grabbing and HMD stuff
    #NOTE: This the background frames is Windows specific
    controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
    #controller.set_policy(Leap.Controller.POLICY_IMAGES)
    #controller.set_policy(Leap.Controller.POLICY_OPTIMIZE_HMD)
    
    
    #initialize listener
    listener = FrameListener()
    controller.add_listener(listener)
    
    #record until told not to
    raw_input('press enter to stop recording')
    
    controller.remove_listener(listener)
    
    print 'writing data to file, and images'
    #write our huge frame list
    listener.writeDataToFile()
    
    