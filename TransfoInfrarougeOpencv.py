#######################################################
# Thermal camera Plotter with AMG8833 Infrared Array
#
# by Joshua Hrisko
#    Copyright 2021 | Maker Portal LLC
#
#######################################################
#
import time,sys
sys.path.append('LibrairieInfra/')
# load AMG8833 module
import amg8833_i2c
import numpy as np
import matplotlib.pyplot as plt
import cv2
from datetime import datetime as dt
import json
#



seuil = 25
p=0
Etat=[[],[],[],[],[]]
dminfixe=2
fr=0
surface=1
config = "config.txt"

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
    #for i in range (1,int(n/2)):
    #    sdeb+=L[i][1]
    #    sfin+=L[n-i][1]
    sdeb=L[0][1]
    sfin=L[-1][1]
    if sdeb>sfin and sdeb>4:
        return -1
    elif sdeb<sfin and sdeb<4:
        return 1
    else:
        return 0
    

L = []
with open(config, 'r') as fichier:
    for line in fichier:
        L.append(line.strip("\n").split("=")[1]) #Ca a l'air compliqué mais ça récupère juste le nom du serveur
        L.append(line.strip("\n").split("=")[1]) #Idem avec le topic
server = L[0]
topic = L[1]

#Définition du client publisher
client = mqtt.Client("Compteur de personne")
client.connect(server)


## Fonctions annexes
def send_mqtt(client, topic, dp):
    """Envoie la donnée dx au sujet topic du serveur mqtt"""
    now=dt.now()
    timestamp=int(dt.timestamp(now))
    dic = {"variation":dp,"timestamp":timestamp}
    client.publish(topic, payload=json.dumps(dic),qos=2)
    print("published",dp)
#####################################
# Initialization of Sensor
#####################################
#
t0 = time.time()
sensor = []
while (time.time()-t0)<1: # wait 1sec for sensor to start
    try:
        # AD0 = GND, addr = 0x68 | AD0 = 5V, addr = 0x69
        sensor = amg8833_i2c.AMG8833(addr=0x69) # start AMG8833
    except:
        sensor = amg8833_i2c.AMG8833(addr=0x68)
    finally:
        pass
time.sleep(0.1) # wait for sensor to settle

# If no device is found, exit the script
if sensor==[]:
    print("No AMG8833 Found - Check Your Wiring")
    sys.exit(); # exit the app if AMG88xx is not found 
#
#####################################
# Start and Format Figure 
#####################################
#
plt.rcParams.update({'font.size':16})
fig_dims = (12,9) # figure size
fig,ax = plt.subplots(figsize=fig_dims) # start figure
pix_res = (8,8) # pixel resolution
zz = np.zeros(pix_res) # set array with zeros first
im1 = ax.imshow(zz,vmin=15,vmax=40) # plot image, with temperature bounds
cbar = fig.colorbar(im1,fraction=0.0475,pad=0.03) # colorbar
cbar.set_label('Temperature [C]',labelpad=10) # temp. label
fig.canvas.draw() # draw figure

ax_bgnd = fig.canvas.copy_from_bbox(ax.bbox) # background for speeding up runs
fig.show() # show figure
#
#####################################
# Plot AMG8833 temps in real-time
#####################################
#
pix_to_read = 64 # read all 64 pixels
client.loop_start()
while True:
    changement=False
    status,pixels = sensor.read_temp(pix_to_read) # read pixels with status
    if status: # if error in pixel, re-enter loop and try again
        continue
    
    T_thermistor = sensor.read_thermistor() # read thermistor temp
    fig.canvas.restore_region(ax_bgnd) # restore background (speeds up run)
    im1.set_data(np.reshape(pixels,pix_res)) # update plot with new temps
    frame=np.reshape(pixels, pix_res)
    im1.set_data(frame)
    ax.draw_artist(im1) # draw image again
    fig.canvas.blit(ax.bbox) # blitting - for speeding up run
    fig.canvas.flush_events() # for real-time plot
    
    binary=cv2.threshold(frame, seuil, 255, cv2.THRESH_BINARY)[1].astype(np.uint8)
    
    contours, nada=cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #positions=np.where(binary>0)
    frame_contour=frame.copy()
    fr+=1
    
    for c in contours:
        cv2.drawContours(frame_contour, [c], 0, (0, 255, 0), 5)     #dessiner les contours
        if cv2.contourArea(c)<surface:      #afficher que les rectangles avec une surface supérieure à celle rentrée
            continue
        x, y, w, h=cv2.boundingRect(c)  #trace les rectangles (le + grand ds le contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        centre.append((int(x+w/2),int(y+h/2)))
    print(centre)
    for i in range (0,5): #Mise à jour de Etat et détection de la fin d'un passage
        if Etat[i][0]!=(-1,-1):
            indmin=trouvemin(centre,Etat[i][-1])
            if indmin==-1:
                if len(Etat[i])>3:
                    dp=sens(Etat[i])
                    p=p+dp#le nb de personnes est fct du sens
                    if dp!=0:
                        send_mqtt(client, topic, dp)
                    EtatImmobileFrame[i]=0
                    Etat[i]=[(-1,-1)]
                EtatImmobileFrame[i]+=1
                if EtatImmobileFrame[i]==5:
                    EtatImmobileFrame[i]=0
                    Etat[i]=[(-1,-1)]
                
            else:
                Etat[i].append(centre[indmin])
                del centre[indmin]
                
    if len(centre)!=0: #Introduction d'un nouvel intrus
        n=-1
        for nouveau in centre:
            n+=1
            i=0
            while Etat[i][0]!=(-1,-1):
                i+=1
                if i==5:
                    break
            Etat[i][0]=nouveau
            del centre[n]
    
    for i in range(0,5): # Dessin de la trace
        if Etat[i][0]!=(-1,-1):
            n=len(Etat[i])
            for j in range(0,n-1):
                cv2.line(frame, Etat[i][j], Etat[i][j+1], (0, 255, 0), 10)
    
    
    cv2.imshow("frame", frame)
    cv2.imshow("seuildiff", binary)
    
    key=cv2.waitKey(20)&0xFF
    #if key==ord('q'):
     #   break
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
    
    
    print(p)# print thermistor temp
    
    