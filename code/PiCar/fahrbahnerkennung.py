#Code basiert auf: https://towardsdatascience.com/deeppicar-part-4-lane-following-via-opencv-737dd9e47c96
#Stand 24.05.2020
import cv2
import numpy as np
import math
import logging

def eckenerkennung(frame):
    #Algorithmus zur Eckenerkennung
    #in anderen farbbereich umwandeln um blau besser herauszufiltern
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #cv2.imwrite('hsv.jpg', hsv)

    #farbereich via trial and error herausgefunden
    lower_blue = np.array([60, 0, 50])
    upper_blue = np.array([140, 255, 200])
    #maske zum Herausfiltern
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    #nur die kanten anzeigen
    edges = cv2.Canny(mask, 200, 400)
    #cv2.imwrite('ecken.jpg', edges)
    return edges

def nur_relevante_Region(edges):
    #problem: eckenerkennung() auch viele in oberer haelfte

    #params intialisieren
    height, width = edges.shape
    mask = np.zeros_like(edges)

    #nur untere Haelfte ist interessant
    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1 / 2),
        (width, height),
        (0, height),
    ]], np.int32)

    #fuellen
    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    #cv2.imwrite('ecken_relevant.jpg', cropped_edges)
    return cropped_edges

def erkenne_Linien_Segmente(cropped_edges):
    #Grundlage: HoughLinesP Function
    #Umwandeln in Polarkoordinaten (kann auch vertikale Linien darstellen)
    rho = 1 #genauigkeit in px
    angle = np.pi / 180 #winkelgenauigkeit in °
    min_threshold = 5 #minimale anzahl an punkten
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold,
                                    np.array([]), minLineLength=3, maxLineGap=2)
    return line_segments

def zwei_Fahrbahnen(frame, line_segments):
    lane_lines = [] #fahrbahn

    if line_segments is None:
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  #grenze: rechtes drittel
    right_region_boundary = width * boundary # grenze: linkes drittel

    #wenn negative steigung --> rechte bahn, positive steigung: linke bahn
    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    #zu fahrbahn zusammenfuehren
    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    return lane_lines

def make_points(frame, line):
    #Hilffunkstion: gitb endpunkte eines linien_segmentes aus
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height
    y2 = int(y1 * 1 / 2)

    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def erkenne_Fahrbahn(bild):
    edges = eckenerkennung(bild)
    cropped_edges = nur_relevante_Region(edges)
    line_segments = erkenne_Linien_Segmente(cropped_edges)
    fahrbahn = zwei_Fahrbahnen(bild, line_segments)

    return fahrbahn

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=2):
    #bild auf video plotten
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

def steuer_winkel(frame, lane_lines):
    height, width, _ = frame.shape

    if len(lane_lines) == 0:
        return -90

    height, width, _ = frame.shape
    y_offset = int(height / 2)
    if len(lane_lines) == 1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
    else:
        #wenn beide linien zu sehen sind
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.02
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid


    angle_to_mid_radian = math.atan(x_offset / y_offset) #dreieck
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi) #konvertieren
    steering_angle = angle_to_mid_deg + 90 #offset wird von PiCar benötigt

    return steering_angle

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):
    #intialisieren
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape

    steering_angle_radian = steering_angle / 180.0 * math.pi
    #bildpunkte berechnen
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = int(height / 2)

    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width) #punkte zu linie zusammenführen
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image

def smooth_steuer_Winkel(curr_steering_angle,
          new_steering_angle,
          num_of_lane_lines,
          max_angle_deviation_two_lines=5,
          max_angle_deviation_one_lane=1):
    if num_of_lane_lines == 2 :
        # if both lane lines detected, then we can deviate more
        max_angle_deviation = max_angle_deviation_two_lines
    else :
        # if only one lane detected, don't deviate too much
        max_angle_deviation = max_angle_deviation_one_lane

    angle_deviation = new_steering_angle - curr_steering_angle
    if abs(angle_deviation) > max_angle_deviation:
        stabilized_steering_angle = int(curr_steering_angle
            + max_angle_deviation * angle_deviation / abs(angle_deviation))
    else:
        stabilized_steering_angle = new_steering_angle
    return stabilized_steering_angle

def main():
    bild = cv2.imread('test.jpg')
    #fahrbahn?
    fahrbahn = erkenne_Fahrbahn(bild)
    lane_lines_image = display_lines(bild, fahrbahn)
    #cv2.imwrite("fahrbahn.jpg", lane_lines_image)
    #wohin?
    steuerWinkel = steuer_winkel(bild, fahrbahn)
    heading_image = display_heading_line(bild, steuerWinkel)
    #cv2.imwrite("fahrlinie.jpg", heading_image)

if __name__ == "__main__":
    main()

#live video anzeigen
def show_image(title, frame):
    cv2.imshow(title, frame)

#um später einfach drauf zuzugreifen
class HandCodedLaneFollower(object):

    #Initialisiere
    def __init__(self, car=None):
        logging.info('Initialisiere PiCar..')
        self.car = car
        self.m_steuer_winkel = 90 #standard

    #gibt bild mit fahrstrecke zurück
    def folge_Fahrbahn(self, bild, orig = False):
        #show_image("Original", frame)

        fahrbahn = erkenne_Fahrbahn(bild)
        finales_bild = self.steuer(bild, fahrbahn)

        if(orig == True):
            return finales_bild
        else:
            return bild
            
    #erzeugt das bild mit der richtung
    def steuer(self, bild, fahrbahn):
        logging.debug('steuer..')
        if len(fahrbahn) == 0:
            logging.error('Keine Farhbahn vorhanden.')
            return bild

        n_steuer_winkel = steuer_winkel(bild, fahrbahn)
        self.m_steuer_winkel = smooth_steuer_Winkel(self.m_steuer_winkel, n_steuer_winkel, len(fahrbahn))

        if self.car is not None:
            self.car.front_wheels.turn(self.m_steuer_winkel)

        wohin_bild = display_heading_line(bild, self.m_steuer_winkel)
        #show_image("Wohin?", curr_heading_image)

        return wohin_bild
