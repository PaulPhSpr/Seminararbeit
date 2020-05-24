#code basiert auf https://towardsdatascience.com/deeppicar-part-5-lane-following-via-deep-learning-d93acdce6110
#Stand 24.05.2020
import cv2
import sys
import os
from fahrbahnerkennung import HandCodedLaneFollower

def speicher_steuerwinkelBild(video_file, orig):
    lane_follower = HandCodedLaneFollower() #erstelle bilderkennung
    cap = cv2.VideoCapture(video_file + '.avi') #Initialisiere

    try:
        i = 0
        while cap.isOpened(): #solange video läuft
            _, frame = cap.read() #lese frame aus
            winkelBild = lane_follower.folge_Fahrbahn(frame, orig) #erstelle fahrbahnbild
            cv2.imwrite("%s_%04d_%04d.png" % (video_file, i, lane_follower.m_steuer_winkel), winkelBild)
            i += 1 #spule ein frame vor in der Bezeichnung
            if cv2.waitKey(1) == ord('q'): #abbrechen bei tastendruck
                break
    finally: #wenn video zu ende
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    print("Start. Dies wird einige Minuten dauern..")
    speicher_steuerwinkelBild(sys.argv[1], sys.argv[2]) #nimmt den ersten und zweiten ausdruck aus cmd als argument
    print("Fertig")
