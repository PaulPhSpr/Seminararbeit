from PIL import Image
import cv2
import os

def crop(ordner, datensatz, pfad):
    #Höhe und Breite
    b, h = Image.open(os.path.join(ordner, datensatz[0])).size

    for i in range(0, len(datensatz)):
        #bild laden
        bild = Image.open(os.path.join(ordner, datensatz[i]))

        #werte angeben
        links = 226
        rechts = b - 226
        oben = 0
        unten = h

        #zuschneiden
        bild_crop = bild.crop((links, oben, rechts, unten))

        #speichern
        bild_crop.save(os.path.join(pfad, datensatz[i]))

def lade(ordner):
    bilder = []

    for name in os.listdir(ordner): #alle dateien durchgehen
        bilder.append(name)

    return bilder

def komprimiere(ordner, datensatz, pfad):
    b, h = Image.open(os.path.join(ordner, datensatz[0])).size
    for i in range(0, len(datensatz)):
        #bild laden
        bild = Image.open(os.path.join(ordner, datensatz[i]))

        #mit ANTIALAS komprimieren
        #gleichzeitig runterskalieren
        bild_neu = bild.resize((b//10, h//10), Image.ANTIALIAS)

        #Speichern
        bild_neu.save(os.path.join(pfad, datensatz[i]), qualitiy = 10, optimize=True)

if __name__ == "__main__":
    orig_ordner = r"D:/Bilder/Seminararbeit/Datensatz_unkomprimiert/"
    crop_ordner = r"D:/Bilder/Seminararbeit/Datensatz_crop/"
    komp_ordner = r"D:/Bilder/Seminararbeit/Datensatz_komp/"

    datensatz = lade(orig_ordner) #array mit string mit allen Bildnamen
    print("Starte Crop Prozess")
    crop(orig_ordner, datensatz, crop_ordner) #crop + zwischenspeichern
    print("Starte Komprimieren")
    komprimiere(crop_ordner, datensatz, komp_ordner) #komprimieren + speichern
    print("Fertig!")
