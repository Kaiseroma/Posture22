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

The algorithm is based on MediaPipe Pose, which is an ML solution for high-fidelity body pose tracking.

The solution proposed by the author of this project is itself a trainable posture classifier. If the end user wants to adjust (improve) the embedded calibration
procedure, it is easy to do this (will be shown later).

# How to launch

1. Download this repository.
2. Open the files as a project in your favorite code editor (in the case of the author, it is Spyder).
3. Before launching the application, make sure you have all the dependencies installed (that is, all necessary libraries).
4. Launch file main.py.
5. Stand tall at some distance between 0.9 and 1.6m from your laptop.
6. See how good or bad your posture is!

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

P.S. The winner model is RandomForestClassifier with score over 0.99 on the test subset:)
