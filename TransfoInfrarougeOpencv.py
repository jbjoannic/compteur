#######################################################
# Thermal camera Plotter with AMG8833 Infrared Array
#
# by Joshua Hrisko
#    Copyright 2021 | Maker Portal LLC
#
#######################################################
#
import time,sys
sys.path.append('../')
# load AMG8833 module
import amg8833_i2c
import numpy as np
import matplotlib.pyplot as plt
import cv2
#



seuil = 25
p=0
Etat=[[],[],[],[],[]]
dminfixe=2
fr=0
surface=1

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
    if sdeb>sfin and sdeb>400:
        return -1
    elif sdeb<sfin and sdeb<400:
        return 1
    else:
        return 0
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
    
    binary=cv2.threshold(frame, seuil, 255, cv2.THRESH_BINARY)[1]
    
    contours, nada=cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    positions=np.where(binary>0)
    frame_contour=frame.copy()
    fr+=1
    
    for c in contours:
        cv2.drawContours(frame_contour, [c], 0, (0, 255, 0), 5)     #dessiner les contours
        if cv2.contourArea(c)<surface:      #afficher que les rectangles avec une surface supérieure à celle rentrée
            continue
        x, y, w, h=cv2.boundingRect(c)  #trace les rectangles (le + grand ds le contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        centre.append((int(x+w/2),int(y+h/2)))
        
    for i in range (0,5): #Mise à jour de Etat et détection de la fin d'un passage
        if Etat[i][0]!=(-1,-1):
            indmin=trouvemin(centre,Etat[i][-1])
            if indmin==-1:
                if len(Etat[i])>3:
                    p=p+sens(Etat[i])   #le nb de personnes est fct du sens
                    Etat[i]=[(-1,-1)]
                    changement=True
                
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
            Etat[i][0]=nouveau
            del centre[n]
    
    for i in range(0,5): # Dessin de la trace
        if Etat[i][0]!=(-1,-1):
            n=len(Etat[i])
            for j in range(0,n-1):
                cv2.line(frame, Etat[i][j], Etat[i][j+1], (0, 255, 0), 10)
    
    
    cv2.imshow("frame", frame)
    cv2.imshow("seuildiff", binary)
    print("Thermistor Temperature: {0:2.2f}".format(T_thermistor)) # print thermistor temp
    
    