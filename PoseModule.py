import cv2
import time
import mediapipe as mp
import math

mp_drawing = mp.solutions.drawing_utils  

# Following examples from https://www.youtube.com/watch?v=brwgBf6VB0I

class poseDetector():
    def __init__(self, mode=False, detect_conf=0.5, track_conf=0.5):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=mode,
            min_detection_confidence=detect_conf,
            min_tracking_confidence=track_conf
        )

    def findPose(self, image, draw=True):
        imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if draw and self.results.pose_landmarks:
            self.mpDraw.draw_landmarks(image, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return image

    def getPosition(self, image, draw=True):
        lmList = {}
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = image.shape  # Gives us relative coords in fractions
                cx, cy = int(lm.x * w), int(lm.y * h)  # Converting to pixels to help draw on the image
                lmList[id] = [cx, cy]
                if draw:
                    cv2.circle(image, (cx, cy), 10, (255, 0, 0), 3)
        return lmList

    def getPositionArrayByIndex(self, image, ids):
        lmList = {}
        if self.results.pose_landmarks:
            mp_drawing.draw_landmarks(image, self.results.pose_landmarks)
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                if id in ids:
                    tid = str(id)
                    lmList[tid + '_x'] = lm.x
                    lmList[tid + '_y'] = lm.y
                    lmList[tid + '_z'] = lm.z
                    lmList[tid + '_v'] = lm.visibility
        return lmList, image
    
    def findAngle(self, img, p1, p2, p3, draw=True):
 
        # Get the landmarks for angle calculation
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]
 
        # Calculate the angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle

def main():
    poser = poseDetector()
    cap = cv2.VideoCapture(0)
    pTime = 0
    while True:
        success, img = cap.read()
        # Timing and FPS computation
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        img = poser.findPose(img, True)
        positions = poser.getPosition(img, False)

        # Showing frame with FPS
        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()