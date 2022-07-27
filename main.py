import cv2
import time

import PoseModule as pm

import pickle
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

xgb_parms = { 
    'max_depth':4, 
    'learning_rate':0.05, 
    'subsample':0.8,
    'colsample_bytree':0.6, 
    'eval_metric':'auc',
    'objective':'binary:logistic',
    'tree_method':'hist',
    'predictor':'cpu_predictor',
    'random_state':42
}

class MainClass():
    def __init__(self, landmarks):
        self.landmarks = landmarks
        self.calibration_data = []  
        self.threshold = 0.0
        self.model = "No model"
        self.latest_breach = False

    def calibrate(self):
        df = pd.DataFrame(self.calibration_data)
        print(df)

        x = df.drop('pose', axis=1)
        y = df['pose']  

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=1234)

        pipelines_list = {
            'rf': make_pipeline(StandardScaler(), RandomForestClassifier()),
            'gb': make_pipeline(StandardScaler(), GradientBoostingClassifier()),
            'xg': make_pipeline(StandardScaler(), XGBClassifier(**xgb_parms))
        }
        
        fitted_models = {}
        for algo, pipeline in pipelines_list.items():
            model = pipeline.fit(x_train, y_train)
            fitted_models[algo] = model

        # Choosing the best model
        top = 0
        for algo, model in fitted_models.items():
            y_hat = model.predict(x_test)
            score = accuracy_score(y_test, y_hat)
            print(algo, score)
            if score >= top:
                self.model = model
                top = score

        with open('model.pkl', 'wb') as f:
            pickle.dump(self.model, f)

    def read_model(self, path="model.pkl"):
        with open('model.pkl', 'rb') as f:
            self.model = pickle.load(f)

    def check_breach(self, data):
        assert isinstance(data, dict)
        df = pd.DataFrame([data])

        pred = self.model.predict(df)[0]
        self.latest_prediction = pred
        if pred == 'slouch':
            self.latest_breach = True
            return True
        else:
            self.latest_breach = False
            return False

    def get_prediction(self):
        return self.latest_prediction

    def add_data(self, data, pose):
        assert isinstance(data, dict)
        data['pose'] = pose
        self.calibration_data.append(data)

if __name__ == '__main__':
    # adopt PoseModule
    poser = pm.poseDetector()
    cap = cv2.VideoCapture(0)
    crits = [ MainClass([0, 7, 8, 11, 12, 23, 24]), ]

    fps_value = 30
    
    train = False  # If false, monitor regime. Set to true if want to improve calibration
    calibration_period_seconds = 600  # If train - how long to calibrate x2

    try:
 
        prev, capture_time = 0, 0
        start_time = time.time()
        
        if train:
            print("Program started, please slouch for {} seconds to calibrate...".format(calibration_period_seconds))
            first_calibration = False
            second_calibration = False
        else:
            print("Monitoring started.")
            first_calibration = True
            second_calibration = True

            # Load already trained models
            [crit.read_model() for crit in crits]

        while True:
            time_elapsed = time.time() - prev
            time_elapsed_total = time.time() - start_time
            res, img = cap.read()

            # Process and get positions
            img = poser.findPose(img, True)
            positions, img = poser.getPositionArrayByIndex(img, [11, 12])

            # Check whether calibration is complete and should switch to monitoring
            if time_elapsed_total > calibration_period_seconds and not first_calibration:
                print("Slouch calibration complete, please stand straight")

                # Set flag of slouch calibration finished
                first_calibration = True

            elif time_elapsed_total > calibration_period_seconds * 2 and not second_calibration:
 
                print("Straight calibration complete, training the model")

                # Calibration procedure
                [crit.calibrate() for crit in crits]

                # Set flag of complete calibration
                print("Calibration complete, monitoring!")
                second_calibration = True

            # FPS limit on processing or passing the image
            if time_elapsed > 1./fps_value :
                prev = time.time()
                # Calibration
                if not first_calibration:  # Calibration ongoing 
                    [crit.add_data(positions, "slouch") for crit in crits]
                elif not second_calibration:
                    [crit.add_data(positions, "straight") for crit in crits]

                # Monitoring regime
                else:
                    crits[0].check_breach(positions)
                    prediction = crits[0].get_prediction()

                    # Draw prediction on the image
                    scaler = 2
                    if prediction == 'straight':
                        color_tuple = (0, 125, 0)
                    else:
                        color_tuple = (0, 0, 125)
                    text_color = (255, 255, 255)

                    cv2.rectangle(img, (0, 0), (250 * scaler, 60 * scaler), color_tuple, -1)
                    cv2.putText(img, 'Pose', (95 * scaler, 12 * scaler), cv2.FONT_HERSHEY_SIMPLEX, 0.5 * scaler, text_color, 1, cv2.LINE_AA)
                    cv2.putText(img, str(prediction), (90 * scaler, 40 * scaler), cv2.FONT_HERSHEY_SIMPLEX, 1 * scaler, text_color, 2, cv2.LINE_AA)

            cv2.imshow('Posture22 Project', img)
            if cv2.waitKey(1) & 0xFF == 27:
                cap.release()
                cv2.destroyAllWindows()
                break

    except KeyboardInterrupt:
        print("\nRequested to stop, stopping")
        cap.release()
        cv2.destroyAllWindows()