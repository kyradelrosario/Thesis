# Thesis
Instructions:
Needs Python 2.7
Install Scipal
Install Numpy
Install CV2
Install matplotlib
Install Argparse
Install Glob

1. Convert videos to frames using an external program
2. Put the frames into a folder
3. Create a file path for the folder using this notation:
	movie = [cv2.imread(file) for file in glob.glob("folder_name/*.png")]
4. Call the keyframe algorithm method on the movie:
	keyframeAlgorithm(movie)
5. Run code.

