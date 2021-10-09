import numpy as np
import cv2
import matplotlib.pyplot as plt

## Choix de l'image'
originalegd=cv2.imread("C:/Users/jean-/Documents/Mines_2A/Protech/algoCompteur/video2_Momentorigin.jpg")
framegd=cv2.imread("C:/Users/jean-/Documents/Mines_2A/Protech/algoCompteur/video2_Moment4.jpg")
## Déclaration des variables

## Initialisation des variables

p=2
mfps=100
Etat=[[],[],[],[],[]] #Stockage des coordonnées des personnes sur la vidéo
kernel_blur=15      #gérer le flou
seuil=50            #sensibilité de détection
surface=70000      #vue de dessus: 70000

plt.imshow(originalegd)
plt.show()

originale= originalegd[:,200:1000] #redimensionnement de la vidéo
frame=framegd[:,200:1000] #[50:250,200:400]  #meme redimensionnement

plt.imshow(originale)
plt.show()
plt.imshow(frame)
plt.show()
dminfixe=300

for i in range(0,5):
    Etat[i].append((-1,-1))
centre=[]

def trouvemin(C,n): #retourne l'indice du voisin s'il y en a un assez proche ou -1 sinon
    min=dminfixe
    indice=-1
    i=-1
    for k in C:
        indice+=1
        d=np.sqrt((n[0]-k[0])**2+(n[1]-k[1])**2)
        if d<min:
            min=d
            i=indice
    return i
        
def sens(L): #retourne 1 si la personne descend et -1 sinon
    n=len(L)
    sdeb=0
    sfin=0
    for i in range (1,int(n/2)):
        sdeb+=L[i][1]
        sfin+=L[n-i][1]
    if sdeb>sfin:
        return -1
    else:
        return 1
    
def disk( radius ): # defines a circular structuring element with radius given by ’ radius ’
    x = np.arange( -radius , radius+1, 1)
    xx, yy = np.meshgrid(x, x)
    d = np.sqrt (xx**2 + yy**2)
    return (d<=radius).astype(np.uint8)



fr=1
originale=cv2.cvtColor(originale, cv2.COLOR_BGR2GRAY)       #noir et blanc, essayer COLOR_BGR2HSV
originale=cv2.GaussianBlur(originale, (kernel_blur, kernel_blur), 0)        #mettre le flou  
kernel_dilate=np.ones((5, 5), np.uint8) #par défaut en float64, la le type en int8
kernel_morphcl=disk(75)
kernel_morphop=disk(15)
    
    

gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
gray=cv2.GaussianBlur(gray, (kernel_blur, kernel_blur), 0)
grays=cv2.threshold(gray, seuil, 255, cv2.THRESH_BINARY)[1]

mask=cv2.absdiff(originale, gray)  #difference absolue
mask=cv2.threshold(mask, seuil, 255, cv2.THRESH_BINARY)[1] #retourne un threshold

mask1=cv2.erode(mask,kernel_dilate, iterations=30) #50 erosions pour enlever les bails
mask1=cv2.dilate(mask1, kernel_dilate, iterations=30) #dilatation

mask2=cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_morphop)
mask2=cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel_morphcl)

mask3=cv2.erode(mask,kernel_dilate, iterations=30)
mask3=cv2.dilate(mask3,kernel_dilate, iterations=30)
mask3=cv2.morphologyEx(mask3, cv2.MORPH_CLOSE, kernel_morphcl)
#mask3=cv2.morphologyEx(mask3, cv2.MORPH_OPEN, kernel_morphop)


contours, nada=cv2.findContours(mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)       #trouver contours, plusieurs fermés
frame_contour=frame.copy()
fr+=1
for c in contours:
    cv2.drawContours(frame_contour, [c], 0, (0, 255, 0), 5)     #dessiner les contours
    if cv2.contourArea(c)<surface:      #afficher que les rectangles avec une surface supérieure à celle rentrée
        continue
    x, y, w, h=cv2.boundingRect(c)  #trace les rectangles (le + grand ds le contour)
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    centre.append((int(x+w/2),int(y+h/2)))
    

    
##Affichage


plt.imshow(frame)
plt.title("frame")
plt.show()

plt.imshow(mask)
plt.title("mask")
plt.show()
#cv2.imshow("contour", frame_contour)
plt.imshow(mask1)
plt.title("mask1")
plt.show()
plt.imshow(mask2)
plt.title("mask2")
plt.show()
plt.imshow(mask3)
plt.title("mask3")
plt.show()


cv2.destroyAllWindows()
