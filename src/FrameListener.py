import Leap, ctypes, struct,numpy, Image, os
'''
Created on Jul 8, 2015
A class that will potentially write Leap frames to file.
Currently also does image frames for use of syncing up with
the eye tracker video. Hypothetically we don't need the 
images and could just use a symbol (like two fingers making peace sign)
to line up video and data stream. This would use much less computing
to file for analysis.

"Since processing the frame takes a bit of time, the images 
from the frame will be at least one camera frame behind 
the images obtained from the controller" - From documentation.
        
@author: Brendan
'''
from main import controller

class FrameListener(Leap.Listener):
    
    prevID = 0
    frameList = []
    imageList = []
    def writeDataToFile(self):
        
        #Use LeapImages as default folder for saving images
        #if it exists make a string that does not exist for new folder
        initialFolderFileString = 'LeapImages'
        folderFileString = initialFolderFileString
        counter = 1
        while (os.path.exists(folderFileString)):
            folderFileString = initialFolderFileString + '_' + counter.__str__()
            counter += 1
        #make dir
        os.mkdir(folderFileString)
        
        #do similar thing with frame.data file
        initialFrameDataString = 'frame'
        frameFileString = initialFrameDataString
        counter = 1
        while (os.path.exists(frameFileString)):
            frameFileString = initialFrameDataString + '_' + counter.__str__()
            counter += 1
        #add .data to end
        frameFileString += '.data'
        
        #for all frames in frameList
        with open(frameFileString, 'wb') as data_file:
            for frame in self.frameList:
                #the commented out code assumes that the frames hold onto the images
                #as they are added to the list. I suspect this is not true
                #as the Image object we use has a pointer to the actual
                #data, which will be long gone by the time we process.
                #thus, I added an imageList that holds ctype_arrays of
                #the raw image data for the left camera and will use that instead.
                
#                 #commented out, potentially won't work
#                 #Grab IR images
#                 leftImage = frame.imageList[0]
#                 rightImage = frame.imageList[1]
#                 
#                 leftImageArray = self.getArrayFromImage(leftImage)
#                 rightImageArray = self.getArrayFromImage(rightImage)
#                 
#                
#                 #supposedly unique frame ID, increases by 1 (or 2 in poor lighting)
#                 #for consecutive frames, can use this for filename
#                 imageId = frame.id
#                 
#                 #write to file
#                 leftImageFileString = folderFileString + '/' + imageId.__str__() + '_left.png'
#                 rightImageFileString = folderFileString + '/' +imageId.__str__() + '_right.png'
#                 
#                 leftImageArray.save(leftImageFileString)
#                 rightImageArray.save(rightImageFileString)


                #implementation that uses list of image data from left camera
                
                #one to one relationship of frameList and imageList
                currIndex = self.frameList.index(frame)
                #get ctype_array from list and convert to numpy array, then to image.
                ctype_array = self.imageList[currIndex]
                numpy_array = numpy.ctypeslib.as_array(ctype_array)
                imageToSave = Image.fromarray(numpy_array)
                
                #supposedly unique frame ID, increases by 1 (or 2 in poor lighting)
                #for consecutive frames, can use this for filename
                imageId = frame.id
                 
                #write to file
                ImageFileString = folderFileString + '/' + imageId.__str__()
                 
                imageToSave.save(ImageFileString)
                
                
                #code from LEAP docs for writing frame to file.
                #writes the size of data black first, then writes the frame data
                #as of now we cannot extract the image data from these serialized 
                #frames. This is a problem, so we save them seperately above this.
                #Real question is can we play this data back?
                #There is code to de serialize it, and Unity/C# code that
                #both records and plays while rendering hands. Would be nice to 'see'
                #the data play in front of you instead of just numbers.
                #Frames should hold all the hand and finger data we need.
                serialized_tuple = frame.serialize
                data = serialized_tuple[0]
                size = serialized_tuple[1]
                data_file.write(struct.pack("i", size))
                
                data_address = data.cast().__long__()
                data_buffer = (ctypes.c_ubyte * size).from_address(data_address)
                data_file.write(data_buffer)
                
    #function taken from LEAP docs that
    #converts image data from a LEAP Image
    #to a numpy array and then makes a PIL image out of it
    def getArrayFromImage(self,image):
        #get the image data pointer, from LEAP doc
        buffer_ptr = image.data_pointer
        ctype_array_def = ctypes.c_ubyte * image.width * image.height

        # as ctypes array
        ctype_array = ctype_array_def.from_address(int(buffer_ptr))
        # as numpy array
        numpy_array = numpy.ctypeslib.as_array(ctype_array)
        retIm = Image.fromarray(numpy_array)
        return retIm
        
    #Simple callback that will
    #add each frame to a list of frames
    def onFrame(self, controller):
        #want to avoid IO here, so
        #we add these things to lists.
        #I'm not worried about frames, but images will likely
        #disappear if not pulled out and added
        self.addFrame(controller)
        
        #add left stereo image data to imageList
        self.addImage(controller.frame().images[0])
        
    #add an image to imageList
    #the image itself is a ctype_array 
    #and can be processed later
    def addImage(self,image):
        buffer_ptr = image.data_pointer
        #define ctype_array (why does multiplication of a ctype with width
        #give an array automatically? That's cool.
        ctype_array_def = ctypes.c_ubyte * image.width * image.height

        #Fill array with data using pointer.
        ctype_array = ctype_array_def.from_address(int(buffer_ptr))
        self.imageList.append(ctype_array)
        
        
    #function that adds current frame to list
    def addFrame(self,controller):
        if controller.frame(1).id() != self.prevID:
            print 'frame was dropped'
            #TODO: deal with dropped frames here
            #as they still exist in history
            #or ignore them because LEAP has
            #high frame rate
        frame = controller.frame() #The latest frame
        self.frameList.append(frame)
        self.prevID = frame.id
    
    
    #function that writes a frame to file given a controller object    
    #likely will not use
    def writeControllerFrame(self, controller):
        #we dropped a frame if the previous frameID doesn't
        #match the last frame this callback processed
        if controller.frame(1).id() != self.prevID:
            print 'dropped frame'
        
        frame = controller.frame() #The latest frame
        
        serialized_tuple = frame.serialize
        serialized_data = serialized_tuple[0]
        serialized_length = serialized_tuple[1]
        data_address = serialized_data.cast().__long__()
        buff = (ctypes.c_ubyte * serialized_length).from_address(data_address)

        self.data_file.write(buff)
        
        self.prevID = frame.id
        
        
    def printPrevID(self):
        print self.prevID