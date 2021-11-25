import paho.mqtt.client as mqtt

config = "config.txt"
effectif_piece = 0

##Récupération des identifiants serveur et topic
L = []
with open(config, 'r') as fichier:
    for line in fichier:
        L.append(line.strip("\n").split("=")[1]) #Ca a l'air compliqué mais ça récupère juste le nom du serveur
        L.append(line.strip("\n").split("=")[1]) #Idem avec le topic

server = L[0]
topic = L[1]
#Définition du client publisher
client = mqtt.Client("Compteur d'entrée")
client.connect(server)


def on_message(client, userdata, message):
    dx = int(message.payload.decode("utf-8"))
    effectif_piece = dx
    print("Received message: ", str(dx))
    
    
client.loop_start()
client.subscribe(topic)
client.on_message = on_message
client.loop_end()