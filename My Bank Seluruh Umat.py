# =============================
#        BANK BSU MODERN
# =============================

import json
import os
import secrets
import time
from datetime import datetime

USER_FILE = "users.json"
DATA_FILE = "accounts.json"
TRANSACTION_FILE = "transactions.json"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# =============================
#            UTIL
# =============================

def garis():
    print("═" * 55)

def header(title):
    print("\n")
    garis()
    print(f"{title.center(55)}")
    garis()

def sukses(msg):
    print(f"✅ {msg}")

def gagal(msg):
    print(f"❌ {msg}")

def info(msg):
    print(f"📌 {msg}")

def load_data(file):
    if not os.path.exists(file):
        return {}

    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def waktu():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def format_rupiah(n):
    try:
        n = int(float(n))
    except:
        n = 0

    return "Rp{:,.0f}".format(n).replace(",", ".")

def parse_rupiah(x):
    try:
        return int(str(x).replace(".", "").replace(",", ""))
    except:
        return 0

def generate_account_number(all_accounts):
    used = set()

    for u in all_accounts.values():
        for a in u:
            used.add(a.get("account_number"))

    while True:
        num = "".join(str(secrets.randbelow(10)) for _ in range(10))

        if num not in used:
            return num

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def find_account(all_acc, nomor):
    nomor = str(nomor)

    for user, accs in all_acc.items():
        for i, acc in enumerate(accs):
            if str(acc.get("account_number")) == nomor:
                return user, i, acc

    return None, None, None

def cek_saldo(saldo, jumlah):
    if jumlah > saldo:
        return False, jumlah - saldo

    return True, 0

# =============================
#         ADMIN PANEL
# =============================

def admin_menu():
    while True:
        data = load_data(DATA_FILE)
        trx = load_data(TRANSACTION_FILE)

        header("🔐 ADMIN PANEL")

        print("1. 👥 Lihat Semua User")
        print("2. 📜 Lihat Semua Transaksi")
        print("3. 🚫 Block / Unblock Akun")
        print("4. 🗑️ Hapus Akun")
        print("5. 🔑 Reset PIN User")
        print("6. 🚪 Logout")

        garis()

        p = input("Pilih Menu : ")

        # ---------- USER ----------
        if p == "1":
            header("📋 DAFTAR USER")

            for user, accs in data.items():
                acc = accs[0]

                status = "🚫 BLOCKED" if acc.get("blocked") else "🟢 ACTIVE"

                print(f"""
👤 Username : {user}
📛 Nama     : {acc['nama']}
🏦 Rekening : {acc['account_number']}
💰 Saldo    : {format_rupiah(acc['saldo'])}
📌 Status   : {status}
                """)

                garis()

        # ---------- TRANSAKSI ----------
        elif p == "2":
            header("📜 SEMUA TRANSAKSI")

            for user, tlist in trx.items():
                for t in tlist:
                    print(
                        f"{t['waktu']} | "
                        f"{user} | "
                        f"{t['tipe']} | "
                        f"{format_rupiah(t['jumlah'])}"
                    )

        # ---------- BLOCK ----------
        elif p == "3":
            u = input("Username : ")

            if u in data:
                data[u][0]["blocked"] = not data[u][0].get("blocked", False)
                data[u][0]["attempt"] = 0

                save_data(DATA_FILE, data)

                sukses("Status akun berhasil diubah")

            else:
                gagal("User tidak ditemukan")

        # ---------- HAPUS ----------
        elif p == "4":
            u = input("Username : ")

            if u in data:
                confirm = input("Yakin hapus akun? (y/n): ")

                if confirm.lower() == "y":

                    del data[u]

                    trx_data = load_data(TRANSACTION_FILE)

                    if u in trx_data:
                        del trx_data[u]

                    users = load_data(USER_FILE)

                    if u in users:
                        del users[u]

                    save_data(DATA_FILE, data)
                    save_data(TRANSACTION_FILE, trx_data)
                    save_data(USER_FILE, users)

                    sukses("Akun berhasil dihapus")

                else:
                    info("Dibatalkan")

            else:
                gagal("User tidak ditemukan")

        # ---------- RESET PIN ----------
        elif p == "5":
            u = input("Username : ")

            if u in data:
                pin = input("PIN Baru : ")

                if pin.isdigit() and len(pin) == 4:
                    data[u][0]["pin"] = pin

                    save_data(DATA_FILE, data)

                    sukses("PIN berhasil direset")

                else:
                    gagal("PIN harus 4 digit")

            else:
                gagal("User tidak ditemukan")

        elif p == "6":
            break

# =============================
#           REGISTER
# =============================

def register():
    users = load_data(USER_FILE)
    data = load_data(DATA_FILE)
    trx = load_data(TRANSACTION_FILE)

    header("📝 REGISTER")

    username = input("Username : ")

    if username in users:
        gagal("Username sudah digunakan")
        return

    password = input("Password : ")
    nama = input("Nama Lengkap : ")
    pin = input("PIN 4 Digit : ")

    if not (pin.isdigit() and len(pin) == 4):
        gagal("PIN tidak valid")
        return

    acc = generate_account_number(data)

    users[username] = {
        "password": password
    }

    data[username] = [{
        "nama": nama,
        "saldo": 0,
        "account_number": acc,
        "pin": pin,
        "blocked": False,
        "attempt": 0
    }]

    trx[username] = []

    save_data(USER_FILE, users)
    save_data(DATA_FILE, data)
    save_data(TRANSACTION_FILE, trx)

    sukses("Register berhasil")

    print(f"""
🏦 Nomor Rekening : {acc}
💰 Saldo Awal     : {format_rupiah(0)}
    """)

# =============================
#            LOGIN
# =============================

def login():
    users = load_data(USER_FILE)

    header("🔐 LOGIN")

    u = input("Username : ")
    p = input("Password : ")

    # ---------- ADMIN ----------
    if u == ADMIN_USER and p == ADMIN_PASS:
        sukses("Admin login berhasil")
        admin_menu()
        return

    if u not in users:
        gagal("Username salah")
        return

    if users[u]["password"] != p:
        gagal("Password salah")
        return

    sukses(f"Welcome {u}")
    menu(u)

# =============================
#          USER MENU
# =============================

def menu(user):
    while True:
        data = load_data(DATA_FILE)
        trx = load_data(TRANSACTION_FILE)

        acc = data[user][0]

        if acc.get("blocked"):
            gagal("AKUN TERKUNCI")
            return

        header("🏦 BANK BSU")

        print(f"👤 User  : {user}")
        print(f"💰 Saldo : {format_rupiah(acc['saldo'])}")

        garis()

        print("1. 💳 Cek Saldo")
        print("2. 💰 Top Up")
        print("3. 💸 Tarik Tunai")
        print("4. 🔄 Transfer")
        print("5. 📜 Mutasi")
        print("6. 👤 Profile")
        print("7. 🔑 Ganti PIN")
        print("8. 🔒 Ganti Password")
        print("9. 🚪 Logout")

        garis()

        p = input("Pilih Menu : ")

        # ---------- SALDO ----------
        if p == "1":
            header("💳 CEK SALDO")
            print(f"Saldo Anda : {format_rupiah(acc['saldo'])}")

        # ---------- TOP UP ----------
        elif p == "2":
            header("💰 TOP UP")

            pin = input("PIN : ")

            if pin != acc["pin"]:
                gagal("PIN salah")
                continue

            print("💰 TOP UP (contoh: 1000000 jangan dikasih titik)")

            jumlah = parse_rupiah(input("Nominal : "))

            data[user][0]["saldo"] += jumlah

            trx[user].append({
                "tipe": "TOP UP",
                "jumlah": jumlah,
                "waktu": waktu()
            })

            save_data(DATA_FILE, data)
            save_data(TRANSACTION_FILE, trx)

            sukses(f"Top up berhasil {format_rupiah(jumlah)}")

        # ---------- TARIK ----------
        elif p == "3":
            header("💸 TARIK TUNAI")

            pin = input("PIN : ")

            if pin != acc["pin"]:
                data[user][0]["attempt"] += 1

                gagal("PIN salah")

                if data[user][0]["attempt"] >= 3:
                    data[user][0]["blocked"] = True

                    gagal("AKUN TERKUNCI")

                save_data(DATA_FILE, data)

                continue

            jumlah = parse_rupiah(input("Jumlah Tarik : "))

            cukup, kurang = cek_saldo(acc["saldo"], jumlah)

            if not cukup:
                gagal(f"Saldo kurang {format_rupiah(kurang)}")
                continue

            data[user][0]["saldo"] -= jumlah

            trx[user].append({
                "tipe": "TARIK",
                "jumlah": jumlah,
                "waktu": waktu()
            })

            save_data(DATA_FILE, data)
            save_data(TRANSACTION_FILE, trx)

            sukses(f"Tarik berhasil {format_rupiah(jumlah)}")

        # ---------- TRANSFER + OTP ----------
        elif p == "4":

            header("🔄 TRANSFER")

            pin = input("PIN : ")

            if pin != acc["pin"]:
                gagal("PIN salah")
                continue

            tujuan = input("Rekening Tujuan : ")

            u2, _, penerima = find_account(data, tujuan)

            if not penerima:
                gagal("Rekening tidak ditemukan")
                continue

            print(f"\n👤 Penerima : {penerima['nama']}")

            jumlah = parse_rupiah(input("Jumlah Transfer : "))

            cukup, kurang = cek_saldo(acc["saldo"], jumlah)

            if not cukup:
                gagal(f"Saldo kurang {format_rupiah(kurang)}")
                continue

            # =============================
            #            OTP
            # =============================

            otp = generate_otp()

            print("\n📨 Mengirim OTP", end="")

            for i in range(3):
                time.sleep(0.5)
                print(".", end="", flush=True)

            print("\n")
            garis()

            print("        🔐 BANK BSU OTP")
            garis()

            print(f"""
Kode OTP Anda :

{otp}

Jangan berikan kode ini kepada siapa pun.
            """)

            garis()

            otp_input = input("Masukkan OTP : ")

            if otp_input != otp:
                gagal("OTP salah, transfer dibatalkan")
                continue

            # =============================
            #      PROSES TRANSFER
            # =============================

            data[user][0]["saldo"] -= jumlah
            data[u2][0]["saldo"] += jumlah

            waktu_now = waktu()

            trx[user].append({
                "tipe": "TRANSFER OUT",
                "jumlah": jumlah,
                "waktu": waktu_now,
                "ke": penerima["nama"]
            })

            trx[u2].append({
                "tipe": "TRANSFER IN",
                "jumlah": jumlah,
                "waktu": waktu_now,
                "dari": acc["nama"]
            })

            save_data(DATA_FILE, data)
            save_data(TRANSACTION_FILE, trx)

            print("\n")

            garis()
            print("        ✅ TRANSFER BERHASIL")
            garis()

            print(f"👤 Dari       : {acc['nama']}")
            print(f"👤 Ke         : {penerima['nama']}")
            print(f"🏦 Rek Tujuan : {tujuan}")
            print(f"💰 Jumlah     : {format_rupiah(jumlah)}")
            print(f"🕒 Waktu      : {waktu_now}")

            garis()

        # ---------- MUTASI ----------
        elif p == "5":
            header("📜 MUTASI TRANSAKSI")

            if not trx[user]:
                info("Belum ada transaksi")

            for t in trx[user]:
                print(
                    f"{t['waktu']} | "
                    f"{t['tipe']} | "
                    f"{format_rupiah(t['jumlah'])}"
                )

        # ---------- PROFILE ----------
        elif p == "6":
            header("👤 PROFILE")

            print(f"""
👤 Nama      : {acc['nama']}
🏦 Rekening  : {acc['account_number']}
💰 Saldo     : {format_rupiah(acc['saldo'])}
            """)

        # ---------- GANTI PIN ----------
        elif p == "7":
            header("🔑 GANTI PIN")

            pin_lama = input("PIN Lama : ")

            if pin_lama != acc["pin"]:
                gagal("PIN lama salah")
                continue

            pin_baru = input("PIN Baru : ")

            if not (pin_baru.isdigit() and len(pin_baru) == 4):
                gagal("PIN harus 4 digit")
                continue

            konfirmasi = input("Konfirmasi PIN : ")

            if pin_baru != konfirmasi:
                gagal("PIN tidak cocok")
                continue

            data[user][0]["pin"] = pin_baru

            save_data(DATA_FILE, data)

            sukses("PIN berhasil diganti")

        # ---------- GANTI PASSWORD ----------
        elif p == "8":
            header("🔒 GANTI PASSWORD")

            users = load_data(USER_FILE)

            pw_lama = input("Password Lama : ")

            if users[user]["password"] != pw_lama:
                gagal("Password lama salah")
                continue

            pw_baru = input("Password Baru : ")

            if len(pw_baru) < 4:
                gagal("Minimal 4 karakter")
                continue

            konfirmasi = input("Konfirmasi Password : ")

            if pw_baru != konfirmasi:
                gagal("Password tidak cocok")
                continue

            users[user]["password"] = pw_baru

            save_data(USER_FILE, users)

            sukses("Password berhasil diganti")

        # ---------- LOGOUT ----------
        elif p == "9":
            sukses("Logout berhasil")
            break

# =============================
#             MAIN
# =============================

def main():
    while True:
        header("🏦 BANK BSU SYSTEM")

        print("1. 📝 Register")
        print("2. 🔐 Login")
        print("3. ❌ Exit")

        garis()

        p = input("Pilih Menu : ")

        if p == "1":
            register()

        elif p == "2":
            login()

        elif p == "3":
            print("\n👋 Terima kasih telah menggunakan BANK BSU\n")
            break

        else:
            gagal("Menu tidak tersedia")

if __name__ == "__main__":
    main()