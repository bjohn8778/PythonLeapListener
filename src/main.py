import Leap,FrameListener
from __builtin__ import int
#from numpy import *

if __name__ == '__main__':
    
    #test Leap
    controller = Leap.Controller()
    
    print 'LEAP connected is ' + controller.is_connected.__str__()
    
    #we want tracking data in background
    #other flags are for image grabbing and HMD stuff
    #NOTE: This the background frames is Windows specific
    controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
    controller.set_policy(Leap.Controller.POLICY_IMAGES)
    #controller.set_policy(Leap.Controller.POLICY_OPTIMIZE_HMD)
    
    #Good for testing one recording but commented out for now
#     #initialize listener
#     listener = FrameListener()
#     controller.add_listener(listener)
#     
#     #record until told not to
#     raw_input('press enter to stop recording')
#     
#     controller.remove_listener(listener)
#     
#     print 'writing data to file, and images'
#     #write our huge frame list
#     listener.writeDataToFile()


    
    
    #init listener, remove and add as recording is needed.
    listener = FrameListener()
    
    #main loop. 
    #should ask the user to enter good/bad grasp, which object, and subject ID
    #if it receives q or quit then end the program. Hitting enter will stop recording.
    #As of now we will write out the files between each object. If speed is an issue we
    #could stop this.
    
    doLoop = True
    while doLoop:
        #first ask for Good/Bad
        #g or b is accepted, or good/bad
        #while ensures that either g or b is entered
        goodString = raw_input('Is this a good or bad grasp? g/b: ')
        while (goodString[0] != 'g' and goodString[0] != 'b'):
            print 'Bad input, try again'
            goodString = raw_input('Is this a good or bad grasp? g/b: ')
        #boolean
        isGood = goodString[0] == 'g'
        
        #try to get an int from input, if it is an int, see if it is in [1,14]
        try:
            objectNum = int(raw_input('Enter object #: '))
        except ValueError:
            print 'invalid object #'
            objectNum = -99
        
        #keep asking until it is valid
        while (objectNum <= 0 or objectNum > 14):
            print 'Bad input, try again'
            try:
                objectNum = int(raw_input('Enter object #: '))
            except ValueError:
                print 'invalid object #'
                objectNum = -99
        
        #can use is digit in this case
        subjectID = raw_input('Enter subject ID #: ')
        while (not subjectID.isdigit()):
            print 'Bad input, try again'
            subjectID = raw_input('Enter subject ID #: ')
        
        
        #build the folder path to save data.
        #initialFolderFileString will be Good/Object#/
        #and initialFrameDataString will be 
        #     Good/Bad_#_S#
        #function will add any numbers needed and data type
        initialFolderFileString = ''
        initialFrameDataString = ''
        
        #Good or bad
        if isGood:
            initialFolderFileString = '/Good/'
            initialFrameDataString = 'Good'
        else:
            initialFolderFileString = '/Bad/'
            initialFrameDataString = 'Bad'
        
        #objectNumber
        initialFolderFileString += str(objectNum) + '/'
        initialFrameDataString += '_' + str(objectNum)
        
        #subjectID
        initialFrameDataString += '_' + subjectID
        
        #have listener write to file 
        print 'Writing to file, please wait'
        listener.writeDataToFile(initialFolderFileString,initialFrameDataString)
        print 'Done writing'
        #keep going?
        doLoop = not raw_input('Enter q to quit, or anything else to continue: ') == 'q'
    