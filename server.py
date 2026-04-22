import socket
from datetime import datetime

HOST = "127.0.0.1"
PORT = 10001
BUFFER_SIZE = 2048
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

clienti_activi = set()
mesaje = []
urmator_id = 1


def este_client_activ(adresa):
    return adresa in clienti_activi


def raspuns_connect(adresa_client):
    if este_client_activ(adresa_client):
        return "ERR | Clientul este deja conectat."

    clienti_activi.add(adresa_client)
    return f"OK | Conectare realizata. Clienti online: {len(clienti_activi)}"


def raspuns_disconnect(adresa_client):
    if not este_client_activ(adresa_client):
        return "ERR | Clientul nu era conectat."

    clienti_activi.remove(adresa_client)
    return "OK | Deconectare realizata."


def raspuns_publish(adresa_client, continut):
    global urmator_id

    if not este_client_activ(adresa_client):
        return "ERR | Trebuie sa te conectezi mai intai."

    text = continut.strip()
    if not text:
        return "ERR | Mesajul trimis este gol."

    mesaj = {
        "id": urmator_id,
        "autor": adresa_client,
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    mesaje.append(mesaj)
    urmator_id += 1

    return f"OK | Mesaj salvat cu id={mesaj['id']}"


def raspuns_delete(adresa_client, argument):
    if not este_client_activ(adresa_client):
        return "ERR | Trebuie sa te conectezi mai intai."

    argument = argument.strip()
    if not argument.isdigit():
        return "ERR | ID invalid."

    id_cautat = int(argument)

    for mesaj in mesaje:
        if mesaj["id"] == id_cautat:
            if mesaj["autor"] != adresa_client:
                return "ERR | Nu poti sterge mesajul altui client."

            mesaje.remove(mesaj)
            return f"OK | Mesajul {id_cautat} a fost sters."

    return f"ERR | Nu exista mesaj cu id={id_cautat}."


def raspuns_list(adresa_client):
    if not este_client_activ(adresa_client):
        return "ERR | Trebuie sa te conectezi mai intai."

    if not mesaje:
        return "OK | Nu exista mesaje inregistrate."

    linii = ["=== MESAJE ==="]
    for mesaj in mesaje:
        linii.append(
            f"[{mesaj['id']}] {mesaj['text']} | {mesaj['timestamp']}"
        )

    return "\n".join(linii)


def proceseaza_cerere(text_primit, adresa_client):
    parti = text_primit.split(" ", 1)
    comanda = parti[0].upper()
    argument = parti[1] if len(parti) > 1 else ""

    if comanda == "CONNECT":
        return raspuns_connect(adresa_client)
    if comanda == "DISCONNECT":
        return raspuns_disconnect(adresa_client)
    if comanda == "PUBLISH":
        return raspuns_publish(adresa_client, argument)
    if comanda == "DELETE":
        return raspuns_delete(adresa_client, argument)
    if comanda == "LIST":
        return raspuns_list(adresa_client)

    return "ERR | Comanda necunoscuta."


print(f"[SERVER] UDP pornit pe {HOST}:{PORT}")

try:
    while True:
        date, adresa = server.recvfrom(BUFFER_SIZE)
        cerere = date.decode("utf-8").strip()

        raspuns = proceseaza_cerere(cerere, adresa)
        server.sendto(raspuns.encode("utf-8"), adresa)

except KeyboardInterrupt:
    print("\n[SERVER] Oprire server.")

finally:
    server.close()
    print("[SERVER] Socket inchis.")
