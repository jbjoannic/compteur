## Compteur de Personne   modif jbjoannic 

## Importation des bibliothèques
import os
import sys
import time
import numpy as np
import cv2
import matplotlib.pyplot as plt

## Choix de la vidéo
#cap=cv2.VideoCapture(0)  #EN GROS LA DEVICE CAM
cap=cv2.VideoCapture("C:/Users/jean-/Documents/Mines_2A/Protech/video2.mp4")

## Déclaration des variables
global p #nb de personne
global dminfixe #distance entre deux voisins (maximale)

## Initialisation des variables

p=2
mfps=100
Etat=[[],[],[],[],[]] #Stockage des coordonnées des personnes sur la vidéo
kernel_blur=15      #gérer le flou
seuil=50            #sensibilité de détection
surface=70000      #vue de dessus: 70000
ret, originalegd=cap.read()   #LIT LES FRAMES, ret boolean et originalegd l'image
print(ret)
plt.imshow(originalegd)
plt.show()
originale= originalegd#[50:250,200:400] #redimensionnement de la vidéo
plt.imshow(originale)
plt.show()
dminfixe=300

for i in range(0,5):
    Etat[i].append((-1,-1))
centre=[]

## Fonctions annexes

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

## Code Principal 
fr=1
originale=cv2.cvtColor(originale, cv2.COLOR_BGR2GRAY)       #noir et blanc, essayer COLOR_BGR2HSV
originale=cv2.GaussianBlur(originale, (kernel_blur, kernel_blur), 0)        #mettre le flou  
kernel_dilate=np.ones((5, 5), np.uint8) #par défaut en float64, la le type en int8
kernel_morphcl=disk(50)
kernel_morphop=disk(15)
#plt.imshow(kernel_morph)
# plt.title("SEmorph")
# plt.show()
div_frame=2
ind=0

while True:
    
    ret, framegd=cap.read()
    if ind%div_frame==0: 
        # if fr == 30:
        #     originale=cv2.cvtColor(framegd, cv2.COLOR_BGR2GRAY)       #noir et blanc, essayer COLOR_BGR2HSV
        #     originale=cv2.GaussianBlur(originale, (kernel_blur, kernel_blur), 0)
            
        tickmark=cv2.getTickCount()  #return le nb de tick depuis un moment precis (ex, le demarrage du kernel)
        frame=framegd #[50:250,200:400]  #meme redimensionnement
        gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        # plt.imshow(gray)
        # plt.title("gray")
        # plt.show()
        
        
        gray=cv2.GaussianBlur(gray, (kernel_blur, kernel_blur), 0)
        # plt.imshow(gray)
        # plt.title("flou")
        # plt.show()
        
        grays=cv2.threshold(gray, seuil, 255, cv2.THRESH_BINARY)[1]
        # plt.imshow(grays)
        # plt.title("seuil simple")
        # plt.show()
        
        
        mask=cv2.absdiff(originale, gray)  #difference absolue
        # plt.imshow(mask)
        # plt.title("difference")
        # plt.show()
        
        mask=cv2.threshold(mask, seuil, 255, cv2.THRESH_BINARY)[1] #retourne un threshold
        # plt.imshow(mask)
        # plt.title("seuil diff {0}".format(fr))
        # plt.show()
        
        mask1=cv2.erode(mask,kernel_dilate, iterations=30) #50 erosions pour enlever les bails
        # plt.imshow(mask)
        # plt.title("erodé")
        # plt.show()
        mask1=cv2.dilate(mask1, kernel_dilate, iterations=30) #dilatation
        # plt.imshow(mask)
        # plt.title("erodé")
        # plt.show()
        
        mask2=cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_morphop)
        # plt.imshow(mask2)
        # plt.title("ouvert diff {0}".format(fr))
        # plt.show()
        mask2=cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel_morphcl)
        # plt.imshow(mask2)
        # plt.title("fermé diff {0}".format(fr))
        # plt.show()
        
        
        
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
            
        #print(Etat)
        # for i in range (0,5): #Mise à jour de Etat et détection de la fin d'un passage
        #     if Etat[i][0]!=(-1,-1):
        #         indmin=trouvemin(centre,Etat[i][-1])
        #         if indmin==-1:
        #             if len(Etat[i])>3:
        #                 p=p+sens(Etat[i])   #le nb de personnes est fct du sens
        #                 Etat[i]=[(-1,-1)]
        #         else:
        #             Etat[i].append(centre[indmin])
        #             del centre[indmin]
                    
        # if len(centre)!=0: #Introduction d'un nouvel intrus
        #     n=-1
        #     for nouveau in centre:
        #         n+=1
        #         i=0
        #         while Etat[i][0]!=(-1,-1):
        #             i+=1
        #         Etat[i][0]=nouveau
        #         del centre[n]
                
        # for i in range(0,5): # Dessin de la trace
        #     if Etat[i][0]!=(-1,-1):
        #         n=len(Etat[i])
        #         for j in range(0,n-1):
        #             cv2.line(frame, Etat[i][j], Etat[i][j+1], (0, 255, 0), 10)
                    
        #originale=gray
        # fps=cv2.getTickFrequency()/(cv2.getTickCount()-tickmark)
        # if mfps>fps:
        #     mfps=fps
            
        ##Affichage
        
        #cv2.putText(frame, "FPS: {:05.2f} [o|l]seuil: {:d}  [p|m]blur: {:d}  [i|k]surface: {:d} p= {:d}".format(mfps, seuil, kernel_blur, surface,p), (10, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 255), 2)
        cv2.imshow("frame", frame)
        cv2.imshow("seuildiff", mask)
        #cv2.imshow("contour", frame_contour)
        cv2.imshow("morphfermé", mask3)
        intrus=0
    ind+=1
    ##Boutons de modification des paramètres
    
    key=cv2.waitKey(20)&0xFF
    if key==ord('q'):
        break
    if key==ord('p'):
        kernel_blur=min(43, kernel_blur+2)
    if key==ord('m'):
        kernel_blur=max(1, kernel_blur-2)
    if key==ord('i'):
        surface+=1000
    if key==ord('k'):
        surface=max(1000, surface-1000)
    if key==ord('o'):
        seuil=min(255, seuil+1)
    if key==ord('l'):
        seuil=max(1, seuil-1)

cap.release()
cv2.destroyAllWindows()



        
