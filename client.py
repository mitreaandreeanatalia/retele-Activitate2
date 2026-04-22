import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 10001
BUFFER_SIZE = 2048
TIMEOUT = 4

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT)

conectat = False

def trimite_la_server(text):
    try:
        sock.sendto(text.encode("utf-8"), (SERVER_IP, SERVER_PORT))
        raspuns, _ = sock.recvfrom(BUFFER_SIZE)
        return raspuns.decode("utf-8")
    except socket.timeout:
        return "ERR | Serverul nu a raspuns la timp."
    except Exception as exc:
        return f"ERR | {exc}"


def validare_comanda(text):
    global conectat

    if not text:
        return False, "ERR | Ai introdus o comanda goala."

    parti = text.split(" ", 1)
    comanda = parti[0].upper()
    argument = parti[1] if len(parti) > 1 else ""

    if comanda in ("PUBLISH", "DELETE", "LIST") and not conectat:
        return False, "ERR | Nu esti conectat."

    if comanda == "PUBLISH" and not argument.strip():
        return False, "ERR | PUBLISH necesita text."

    if comanda == "DELETE" and not argument.strip().isdigit():
        return False, "ERR | DELETE necesita un ID numeric."

    return True, ""


print("=" * 50)
print("CLIENT UDP - varianta personala")
print("Comenzi: CONNECT | DISCONNECT | PUBLISH <text> | DELETE <id> | LIST | EXIT")
print("=" * 50)

try:
    while True:
        comanda = input(">>> ").strip()

        if comanda.upper() == "EXIT":
            print("Client inchis.")
            break

        ok, mesaj_validare = validare_comanda(comanda)
        if not ok:
            print(mesaj_validare)
            continue

        raspuns = trimite_la_server(comanda)
        print(raspuns)

        if comanda.upper() == "CONNECT" and raspuns.startswith("OK"):
            conectat = True
        elif comanda.upper() == "DISCONNECT" and raspuns.startswith("OK"):
            conectat = False

except KeyboardInterrupt:
    print("\nClient intrerupt de utilizator.")

finally:
    sock.close()
    print("Socket inchis.")
