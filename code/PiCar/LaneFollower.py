import cv2
import numpy as np
import logging
import math
from PIL import Image
import tensorflow as tf
import time

#Klasse fuer Steuerung
class LaneFollower(object):
    #Initialisierung
    def __init__(self,
                 car=None,
                 model_path = "cnn.h5"):
        logging.info('Erstelle PiCar...')

        self.car = car
        self.curr_steering_angle = 90 #Initialisierung
        self.model = tf.keras.models.load_model(model_path)

    def follow_lane(self, frame):
        #Steuerung
        self.curr_steering_angle = self.compute_steering_angle(frame)
        logging.debug("Steuerwinkel = %d" % self.curr_steering_angle)

        if self.car is not None:
            self.car.front_wheels.turn(self.curr_steering_angle)

        return self.curr_steering_angle

    def compute_steering_angle(self, frame):
        #Winkel berechnen
        preprocessed = img_preprocess(frame)
        logging.info("Starte")
        steering_angle = self.model.predict(preprocessed, batch_size=len(preprocessed)) #eigentliche steuerwinkelerkennung
        logging.info("Fertig")
        #time.sleep(.5) #für 0,5 Sekunden warten für Verzögerung, da Kamera nicht weitwinkelig genug
        steering_angle = inWinkel(kategorisch_zu_numerisch(steering_angle))

        return steering_angle

def kategorisch_zu_numerisch(y):
    max = 0
    y = y[0]
    for i in range(len(y)):
        if(y[i] > y[max]):
            max = i
    return max

def inWinkel(y):
    return y * 10

def img_preprocess(bild):
    #Richtige dimensionen für CNN
    bild = cv2.resize(bild, (54, 73))
    #Standarsieren
    bild = Image.fromarray((bild).astype(np.uint8)) #nur dieses Dateiformat wird von Pillow akzeptiert
    bild = cv2.cvtColor(np.array(bild), cv2.COLOR_BGR2RGB) #in numpy bild umwandeln
    bild = bild[32:,:] #nur untere haelfte relevant
    bild = np.expand_dims(bild, axis=0) #weil 4 dimensionen erwartet werden
    return bild
