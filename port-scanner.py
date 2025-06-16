import socket
import threading
from datetime import datetime

results = []

target = input("Enter target IP or hostname: ")
try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print("Invalid hostname")
    exit()

start_port = int(input("Enter starting port: "))
end_port = int(input("Enter ending port: "))

# TCP Scanner with banner grabbing
def scan_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            try:
                banner = sock.recv(1024).decode().strip()
            except:
                banner = "No banner"
            print(f"[TCP] Port {port} is open | Banner: {banner}")
            results.append((port, "open", banner))
        sock.close()
    except socket.error:
        pass

# UDP Scanner
def scan_udp_port(port):
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(1)
        udp_sock.sendto(b"", (target_ip, port))
        data, _ = udp_sock.recvfrom(1024)
        print(f"[UDP] Port {port} is open (received response)")
        results.append((port, "udp-open", "Response received"))
    except socket.timeout:
        print(f"[UDP] Port {port} is open|filtered (no response)")
        results.append((port, "udp-filtered", "No response"))
    except Exception:
        pass
    finally:
        udp_sock.close()

# Start scanning
print(f"\nStarting scan on {target_ip}...\n")
start_time = datetime.now()
threads = []

# TCP scan
for port in range(start_port, end_port + 1):
    t = threading.Thread(target=scan_port, args=(port,))
    threads.append(t)
    t.start()

# UDP scan
for port in range(start_port, end_port + 1):
    t = threading.Thread(target=scan_udp_port, args=(port,))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

end_time = datetime.now()
print(f"\nScan completed in {end_time - start_time}")

# Save results to text file
with open("scan_results.txt", "w") as f:
    for port, status, banner in results:
        f.write(f"Port {port} is {status} | {banner}\n")
print("Results saved to scan_results.txt")

# Save results to HTML snippet
with open("scan_results.html", "w") as f:
    f.write("<ul>\n")
    for port, status, banner in results:
        f.write(f"<li>Port {port} is {status} — {banner}</li>\n")
    f.write("</ul>")
print("HTML output saved to scan_results.html")
