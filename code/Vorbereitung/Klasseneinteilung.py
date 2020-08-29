import sys
import os
from sklearn.model_selection import train_test_split
import shutil

#Globale Variablen
dir_inp = "D:\\+Bilder\\Seminararbeit\\Datensatz_komp"
dir_out = "D:\\+Bilder\\Seminararbeit\\Datensatz"
train_dir = "train"
valid_dir = "valid"

#Für die Klasseneinteilung
class_deg = 10
count = (180 // class_deg) + 1

def main():
    print("Der Prozess hat gestartet. Bitte warten..")
    #Output verzeichnis erstellen
    try:
        os.mkdir(dir_out)
    except FileExistsError:
        print("Output Verzeichnis existiert bereits.")

    #in Trainingsdaten und Testdaten aufteilen
    X_train, X_valid, y_train, y_valid = vorbereitung() #Label erst einmal unwichtig
    print("Trainingsdaten: %d\nValidierungsdaten: %d" % (len(X_train), len(X_valid)))

    #in Klassen einteilen
    erstelleOrdner()
    Z_train, z_train = teileInArray(X_train, y_train)
    Z_valid, z_valid = teileInArray(X_valid, y_valid)

    #in entsprechende Ordner kopieren
    kopiereInOrdner(Z_train, True)
    kopiereInOrdner(Z_valid, False)

    print("Fertig!")

def kopiereInOrdner(X, istTrainSet):
    #Wo abspeichern
    if istTrainSet:
        dir = train_dir
    else:
        dir = valid_dir
    dir_fin = os.path.join(dir_out, dir)

    #jede Klasse durchgehen
    for i in range(count):
        #jeden Dateipfad durchgehen
        out = "class" + str(i+1)
        for dat in X[i]:
            shutil.copy(dat, os.path.join(dir_fin, out))

def teileInArray(X, y):
    A = [[] for i in range(count)]
    b = [[] for i in range(count)]
    for i in range(0, len(X)):
        num = int(y[i]/class_deg) + 1 #Klassen von 1 bis 10
        A[num - 1].append(X[i]) #aber indizes von 0 bis 9
        b[num - 1].append(y[i])
    return A, b

def erstelleOrdner():
    try:
        os.mkdir(os.path.join(dir_out, train_dir))
        os.mkdir(os.path.join(dir_out, valid_dir))
        for i in range(1, count+1):
            os.mkdir(os.path.join(dir_out, train_dir, "class" + str(i)))
            os.mkdir(os.path.join(dir_out, valid_dir, "class" + str(i)))
    except FileExistsError:
        print("Klassenverzeichnisse existeren bereits.")

def vorbereitung():
    dat_dir = os.listdir(dir_inp)

    steuerwinkel = []
    bilder_dir = []
    dat_typ = "*.png"

    #Bilder Verzeichnis füllen
    for dat in dat_dir:
        bilder_dir.append(os.path.join(dir_inp, dat))
        winkel = int(dat[-8:-4]) #videoN_FFFF_WWWW.png
        steuerwinkel.append(winkel)

    #in Trainings und Validierungsdaten aufteilen
    X_train, X_valid, y_train, y_valid = train_test_split(bilder_dir, steuerwinkel, test_size=0.2)
    return X_train, X_valid, y_train, y_valid

if __name__ == "__main__":
    main()
