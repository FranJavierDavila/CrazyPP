#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueba real de TURN Allocate (RFC 5766, credenciales long-term) contra Open Relay.

Flujo: Allocate sin auth -> 401 (NONCE/REALM) -> Allocate con USERNAME/REALM/NONCE/
REQUESTED-TRANSPORT/MESSAGE-INTEGRITY (HMAC-SHA1, clave = MD5(user:realm:pass)).
Éxito => respuesta 4.x con XOR-RELAYED-ADDRESS (+ LIFETIME, XOR-MAPPED-ADDRESS).

Uso: python3 test_turn_allocate.py [host] [port] [user] [pass]
"""
import hashlib
import hmac
import os
import socket
import struct
import sys
import time

MAGIC = 0x2112A442

# Tipos de mensaje
ALLOCATE = 0x0003
CLS_SUCCESS = 0x0100  # clase success sobre método base
# (success: method | 0x0100; error: method | 0x0110)

# Atributos
ATTR_USERNAME = 0x0006
ATTR_MI = 0x0008
ATTR_ERROR = 0x0009
ATTR_REALM = 0x0014
ATTR_NONCE = 0x0015
ATTR_XOR_RELAYED = 0x0016
ATTR_REQ_TRANSPORT = 0x0019
ATTR_XOR_MAPPED = 0x0020
ATTR_LIFETIME = 0x000D


def pad4(b: bytes) -> bytes:
    return b + b"\x00" * ((4 - len(b) % 4) % 4)


def attr(t: int, v: bytes) -> bytes:
    return struct.pack("!HH", t, len(v)) + pad4(v)


def xor_addr(raw: bytes, txid: bytes):
    """raw: familia(1)+puerto_xor(2)+addr_xor(4). Devuelve (ip, port)."""
    port = struct.unpack("!H", raw[1:3])[0] ^ (MAGIC >> 16)
    xaddr = struct.unpack("!I", raw[3:7])[0] ^ MAGIC
    ip = ".".join(str((xaddr >> s) & 0xFF) for s in (24, 16, 8, 0))
    return ip, port


def parse_attrs(data: bytes):
    """Devuelve dict tipo->bytes (valor sin padding)."""
    out = {}
    off = 0
    while off + 4 <= len(data):
        t, ln = struct.unpack("!HH", data[off:off + 4])
        val = data[off + 4:off + 4 + ln]
        out[t] = val
        off += 4 + pad4(b"\x00" * ln).__len__() if False else 4 + ((ln + 3) // 4) * 4
    return out


def build_allocate(txid: bytes, creds=None):
    """creds = (username, realm, nonce, password) para el 2º Allocate."""
    attrs = attr(ATTR_REQ_TRANSPORT, b"\x11\x00\x00\x00")  # UDP 17
    mi_needed = False
    if creds:
        username, realm, nonce, password = creds
        attrs += attr(ATTR_USERNAME, username.encode())
        attrs += attr(ATTR_REALM, realm.encode())
        attrs += attr(ATTR_NONCE, nonce.encode())
        attrs += attr(ATTR_REQ_TRANSPORT, b"\x11\x00\x00\x00")
        mi_needed = True
    hdr_len = len(attrs) + (24 if mi_needed else 0)  # MI attr = 4+20
    msg = struct.pack("!HHI", ALLOCATE, hdr_len, MAGIC) + txid + attrs
    if mi_needed:
        # MESSAGE-INTEGRITY: HMAC-SHA1 con longitud de cabecera ya ajustada,
        # calculada sobre el mensaje hasta (excl.) el valor de MI.
        key = hashlib.md5(
            f"{username}:{realm}:{password}".encode()
        ).digest()
        mi_placeholder = struct.pack("!HH", ATTR_MI, 0x0014) + b"\x00" * 20
        base = msg + mi_placeholder[:4]
        mac = hmac.new(key, base, hashlib.sha1).digest()
        msg = base + mac
    return msg


def attempt(host: str, port: int, user: str, password: str) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(5.0)
    try:
        txid1 = os.urandom(12)
        s.sendto(build_allocate(txid1), (host, port))
        try:
            data, _ = s.recvfrom(2048)
        except socket.timeout:
            print(f"  [{host}:{port}] sin respuesta (UDP saliente posiblemente bloqueado)")
            return False
        mtype, mlen, magic = struct.unpack("!HHI", data[:8])
        if mtype != (ALLOCATE | 0x0110):  # error esperado 401
            print(f"  [{host}:{port}] respuesta inesperada type=0x{mtype:04x}")
            return False
        a = parse_attrs(data[8:8 + mlen])
        if 0x0011 not in a:  # ERROR-CODE
            print(f"  [{host}:{port}] 401 sin ERROR-CODE: attrs={list(a)}")
            return False
        ec = a[0x0011]
        code = (ec[1] & 0x07) * 100 + ec[2]
        nonce = a.get(ATTR_NONCE, b"").decode(errors="replace")
        realm = a.get(ATTR_REALM, b"").decode(errors="replace")
        print(f"  [{host}:{port}] 1er Allocate -> {code} realm='{realm}' nonce={nonce[:16]}…")
        if code != 401 or not nonce or not realm:
            print(f"  [{host}:{port}] no es un 401 usable")
            return False
        # 2º Allocate autenticado
        txid2 = os.urandom(12)
        msg = build_allocate(txid2, (user, realm, nonce, password))
        s.sendto(msg, (host, port))
        try:
            data, _ = s.recvfrom(2048)
        except socket.timeout:
            print(f"  [{host}:{port}] 2º Allocate sin respuesta")
            return False
        mtype, mlen, magic = struct.unpack("!HHI", data[:8])
        a2 = parse_attrs(data[8:8 + mlen])
        if mtype == (ALLOCATE | 0x0100):
            relay = a2.get(ATTR_XOR_RELAYED)
            mapped = a2.get(ATTR_XOR_MAPPED)
            life = a2.get(ATTR_LIFETIME)
            r = xor_addr(relay, txid2) if relay and len(relay) >= 8 else None
            m = xor_addr(mapped, txid2) if mapped and len(mapped) >= 8 else None
            lf = struct.unpack("!I", life)[0] if life and len(life) == 4 else None
            print(f"  [{host}:{port}] ✅ ALLOCATE OK — relé asignado {r[0]}:{r[1]}"
                  f" · mapped {m[0]}:{m[1]}" if m else
                  f"  [{host}:{port}] ✅ ALLOCATE OK — relé {r}")
            if lf:
                print(f"    lifetime={lf}s")
            return True
        ecode = None
        if 0x0011 in a2:
            e = a2[0x0011]
            ecode = (e[1] & 0x07) * 100 + e[2]
        print(f"  [{host}:{port}] ❌ 2º Allocate falló type=0x{mtype:04x} err={ecode}")
        return False
    finally:
        s.close()


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "openrelay.metered.ca"
    user = sys.argv[3] if len(sys.argv) > 3 else "openrelayproject"
    password = sys.argv[4] if len(sys.argv) > 4 else "openrelayproject"
    ports = [int(sys.argv[2])] if len(sys.argv) > 2 else [80, 443]
    print(f"TURN Allocate real -> {host} puertos {ports} user='{user}'")
    ok = False
    for p in ports:
        try:
            if attempt(host, p, user, password):
                ok = True
        except OSError as e:
            print(f"  [{host}:{p}] error de red: {e}")
        time.sleep(0.3)
    print("RESULTADO:", "TURN OPERATIVO ✅" if ok else "SIN RELÉ DISPONIBLE ❌")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
