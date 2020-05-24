import imageio
import sys

vid = sys.argv[1]
quell_dir = vid + '.mp4'
ziel_dir = vid + '.avi'

leser = imageio.get_reader(quell_dir)
fps = leser.get_meta_data()['fps']
schreiber = imageio.get_writer(ziel_dir, fps=fps)

print("Starte Konvertieren. Dies kann einige Minuten dauern..")
for bild in leser:
    schreiber.append_data(bild[:, :, :])
schreiber.close()
print("Fertig!")
