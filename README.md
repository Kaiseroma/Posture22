# Posture22
Computer Vision project

# Description

This repository contains Posture22 project. Its aim is to detect whether the posture of a person is correct or not (that is, needs to be changed to a normal one).
The code utilizes the PC (laptop) embedded camera as the information acquisition source.
The algorithm used in this project is designed to detect a posture of a person STANDING at various distances from the camera.

It can detect different types of posture breaches, such as:
- neck inclination from front view;
- torso inclination from front view;
- neck and torso inclination from side view.

The algorithm DOES NOT WORK if the person's shoulders are not present in camera view, as the presence and position of person is detected by shoulders.

The solution proposed by the author of this project is itself a trainable posture classifier. If the end user wants to adjust (improve) the embedded calibration
procedure, it is easy to do this (will be shown later).

# Methodologies

The algorithm is based on MediaPipe Pose, which is an ML solution for high-fidelity body pose tracking, inferring 33 3D landmarks and background segmentation mask on
the whole body from RGB video frames. Digging more deeply, the solution utilizes a two-step detector-tracker ML pipeline. Using a detector, the pipeline first locates 
the person/pose region-of-interest (ROI) within the frame. The tracker subsequently predicts the pose landmarks and segmentation mask within the ROI using the ROI-
cropped frame as input. For video use cases, the detector is invoked only as needed, i.e., for the very first frame and when the tracker could no longer 
identify body pose presence in the previous frame. For other frames the pipeline simply derives the ROI from the previous frame’s pose landmarks.
As it was stated before, the landmark model in MediaPipe Pose predicts the location of 33 pose landmarks (see figure below).

![image](https://user-images.githubusercontent.com/60993883/187292141-de64900c-0465-4dca-b3a8-16411db9e7e5.png)

With that, the file called PoseModule.py was built based on the source code provided by the developers of MediaPipe Pose.

In the project, the points with numbers 0, 7, 8, 9, 11, 12, 23 and 24 are used to derive the prediction of the human object's posture. Among these, points 11 and 12
are used for the object detection as well.

In file main.py it can clearly be seen that the code works in the following way: during the calibration procedure, the algorithm gathers the data standing for the
positions of the landmarks, labeling the first part as "slouch", second as "straight" (which means that in this case we deal with binary classification problem).
Then, data is being normalized and fed to three different types of classifiers, which are: RandomForestClassifier, GradientBoostingClassifier and XGBClassifier. 
Accuracy test is then taken for all three classifiers, and the best model is then saved. As practice shows for now, winning model is actually RandomForestClassifier 
with the standard parameters (of course, this is a field for improvement). The obtained classifier is then used to derive predictions about the posture in the
monitoring regime.

# How to launch

1. Open the files as a project in your favorite code editor (in the case of the author, it is Spyder).
2. Before launching the application, make sure you have all the dependencies installed (that is, all necessary libraries).
3. Launch file main.py.
4. Stand tall at some distance between 0.9 and 1.6m from your laptop.
5. See how good or bad your posture is!

# How to change the calibration procedure

At line 149 of main.py, there is a flag called "train". By default it is set to False, which enables just monitor regime (that is, you are just using the developed
software as is). If set to True, the flag enables to train the posture classifier. You will have to design your calibration procedure by yourself, but this procedure
shall be constrained to the parameter "calibration_period_seconds" set at line 150 (default preset is 600). This parameter defines the time, during which the end user
will have to slouch during the recalibration process. After slouching for calibration_period_seconds period, the end user will also have to stand straight in different
possible poses for the same period. After standing straight for calibration_period_seconds period, the software enters the just monitor regime, but using a new posture
classifier.

# The calibration procedure provided by author of the project

1. Start some timer. We will start calibration from the front view.
2. Inclinate the neck to the left significantly. Beginning from the distance of 0.9m, each 5 seconds step back for ~5cm, until timer shows 75 seconds (in space, this
will equal 1.6m distance from camera).
3. Inclinate the neck to the right significantly. Beginning from the distance of 1.6m, each 5 seconds step forward for ~5cm, until timer shows 150 seconds (in
space, this will equal 0.9m distance from camera).
4. Inclinate the shoulders to the left significantly. Beginning from the distance of 0.9m, each 5 seconds step back for ~5cm, until timer shows 225 seconds (in
space, this will equal 1.6m distance from camera).
5. Inclinate the shoulders to the right significantly. Beginning from the distance of 1.6m, each 5 seconds step forward for ~5cm, until timer shows 300 seconds (in
space, this will equal 0.9m distance from camera).
6. Now we move to the side view. Turn 90 degrees right. Start slouching in different ways (using only head, or also shoulders, or even your whole back) significantly.
Beginning from the distance 0.9m, each 10 seconds take steps right, until timer shows 450 seconds (in space, this will equal 1.6m distance from camera).
7. Turn 180 degrees. Slouch in different ways significantly. Beginning from the distance 1.6m, each 10 seconds take steps right, until timer shows 600 seconds (in
space, this will equal 0.9m distance from camera).
8. After you see the command from Python console to stand straight, start standing straight. For first 5 minutes, stay in front view. Each 10 seconds step back for
~5cm, until the timer shows 750 seconds (in space, this will equal 1.6m distance from camera). Then start stepping forward for ~5cm each 10 seconds, until timer
shows 900 seconds (in space, this will equal 0.9m distance from camera). Here, the author also introduced small inclinations while standing in normal way, so that the
model can understand that not every single inclination is necessarily a slouch.
9. Turn 90 degrees right. Make sure you are standing straight. Beginning from the distance 0.9m, each 10 seconds take steps right, until timer shows 1050 seconds 
(in space, this will equal 1.6m distance from camera).
10. Turn 180 degrees. Beginning from the distance 1.6m, each 10 seconds take steps right, until the timer shows 1200 seconds (in space, this will equal 0.9m 
distance from camera). Calibration finished! This one takes 20 minutes, so don't forget to set train=False next time you use the software.

# Comments
There is still a lot to improve though. For instance, end user can see some bugs when testing the software for front-view neck inclination detection precision (yes,
sometimes it does not show slouch when there is one). The main issue here is calibration procedure. If one does the calibration strictly according to the rules above, 
there can be the following problem: the precision of the algorithm might significantly decrease on distances other than 0.9, 0.95, 1, 1.05m etc. What the author
actually did, is the smooth motion in given interval of distances (somehow still sticking to strict rules though). This smoothes the precision distribution over
distance from camera, however, this also implies loss of quantity of training samples per each distance point, which might sometimes lead to bugs. To solve this,
one might think of increasing the time for each calibration step, however, the overall precision might therefore not increase, because of the human factor: if a 
person, who does the calibration, gets tired - this might actually have a bad impact on the work of the software. Also, because of the human factor, there can be a 
disbalance between the estimation results for right and left inclination from the front view, or disbalance between the results for left-side and right-side views. 
Some of these disbalances can be experienced by the end user right now as well, but, as the author said before, there is always a lot to improve!

