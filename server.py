#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
import time
import urllib.parse

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:
    Cipher = algorithms = modes = None


HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", os.environ.get("SSPA_PORT", "8888")))
PUBLIC_BASE_URL = (
    os.environ.get("SSPA_PUBLIC_BASE_URL")
    or os.environ.get("RENDER_EXTERNAL_URL")
    or f"http://127.0.0.1:{PORT}"
).rstrip("/")

ROOT = os.path.dirname(os.path.abspath(__file__))

# Esta chave fica somente para o protocolo/API que já funcionava antes.
# NÃO é usada nos arquivos .bin.
API_KEY = b"X_i856Ub8utigtyPusy3P4ZQLCbHvTCe"

MANIFEST_VERSION = 202

ASSET_MAP = {
    "URLs": "url.bin",
    "ComebackAttendanceData": "cad.bin",
    "GameConfigData": "gcd.bin",
    "LanguageData": "lgd.bin",
    "LocaleData": "lcd.bin",
    "LocalePopupData": "lpd.bin",
    "ExtraResourceData": "erd.bin",

    "ThemeData": "tmd.bin",
    "ThemeTypeData": "ttd.bin",

    "ArtistData": "atd.bin",
    "MajorGroupData": "mgd.bin",
    "GroupData": "grd.bin",
    "ProfileData": "prd.bin",

    "MusicData": "msd.bin",

    "CardGradeBonusData": "cgd.bin",
    "CardBalanceData": "cbd.bin",
    "CardData": "cdd.bin",
    "CardSellData": "csd.bin",
    "CardIntensifyData": "cid.bin",
    "SelectCardData": "scd.bin",

    "CommonData": "cmm.bin",
    "InputCharRangeData": "icd.bin",
    "HiddenGameData": "hgd.bin",

    "LeagueWeeklyInfoData": "lwi.bin",
    "LeagueWeeklyRewardData": "lwr.bin",
    "DalcomStageRewardData": "slr.bin",

    "NpcData": "npd.bin",

    "AttendanceData": "add.bin",
    "AttendanceConsecutiveData": "acd.bin",

    "SpecialUserData": "sur.bin",

    "CardStoreData": "cds.bin",
    "CardInvenExpandStoreData": "ces.bin",
    "HeadphoneStoreData": "hps.bin",
    "RhythmPointStoreData": "rps.bin",
    "RecommendStoreData": "rcs.bin",
    "SpecialStoreData": "dcs.bin",
    "PopupStoreData": "sts.bin",
    "DiamondStoreData": "dis.bin",

    "IntensifyEventData": "itd.bin",
    "CashPurchaseEventData": "ced.bin",
    "UpdateNoticeData": "und.bin",
    "WordFilterData": "wfd.bin",

    "CollectEventData": "cet.bin",
    "MissionDetailData": "mdd.bin",
    "MissionData": "mss.bin",

    "ExtraNewsData": "end.bin",
    "PopupHelpData": "php.bin",
}


def now_ms():
    return int(time.time() * 1000)


def ok(result=None):
    return {
        "code": 0,
        "result": result,
        "invoke": []
    }


def fail(code, result=None):
    return {
        "code": code,
        "result": result,
        "invoke": []
    }


def asset_file(name):
    filename = ASSET_MAP.get(name)
    if not filename:
        return None

    path = os.path.join(ROOT, filename)

    if not os.path.isfile(path):
        return None

    return path


def asset_version(filename):
    path = os.path.join(ROOT, filename + ".ver")

    if not os.path.isfile(path):
        return 0

    try:
        with open(path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def asset_context():
    base = PUBLIC_BASE_URL + "/assets/"

    ctx = {
        "CdnAddress": {
            "file": base,
            "version": 1
        }
    }

    for logical_name, filename in ASSET_MAP.items():

        # Não anuncia arquivos que não possuímos.
        if not os.path.isfile(os.path.join(ROOT, filename)):
            continue

        ctx[logical_name] = {
            "file": base + urllib.parse.quote(logical_name, safe=""),
            "version": asset_version(filename)
        }

    return {
        "version": MANIFEST_VERSION,
        "context": ctx
    }


def decrypt_api(raw, iv_text):
    if Cipher is None:
        raise RuntimeError(
            "cryptography não instalado. Rode: pip install cryptography"
        )

    iv = iv_text.encode("utf-8")

    if len(iv) != 16:
        raise ValueError("X-SuperStar-AES-IV precisa ter 16 bytes")

    decryptor = Cipher(
        algorithms.AES(API_KEY),
        modes.CBC(iv)
    ).decryptor()

    plain = decryptor.update(base64.b64decode(raw))
    plain += decryptor.finalize()

    # PKCS7
    if plain:
        pad = plain[-1]
        if 1 <= pad <= 16:
            plain = plain[:-pad]

    return plain


def handle_api(req):
    clazz = req.get("class", "")
    method = req.get("method", "")
    params = req.get("params") or []

    if clazz == "Platform":

        if method == "getTimestamp":
            return ok(now_ms())

        if method == "getClientIP":
            return ok("127.0.0.1")

        if method == "checkAssetBundle":
            return ok(asset_context())

    if clazz == "Account" and method in (
        "login",
        "loginSNS",
        "createAccount",
        "createSNSAccount"
    ):
        return ok({
            "authObjectID": 1,
            "specialUserCode": 0,
            "nickname": "SSPA Private",
            "accessToken": "sspa-private-token",
            "user": {
                "objectID": 1,
                "nickname": "SSPA Private",
                "diamond": 2147483647,
                "freeDiamond": 2147483647,
                "rhythmPoint": 2147483647,
                "freeRhythmPoint": 2147483647,
                "headphone": 2147483647,
                "freeHeadphone": 2147483647,
                "dalcomCoin": 2147483647,
                "freeDalcomCoin": 2147483647,
                "themeChanger": 2147483647,
                "nicknameChanger": 2147483647,
                "maxCardInvenCount": 9999
            }
        })

    if clazz == "Account" and method == "getUserData":
        return ok({
            "user": {
                "objectID": 1,
                "nickname": "SSPA Private",
                "diamond": 2147483647,
                "freeDiamond": 2147483647,
                "rhythmPoint": 2147483647,
                "freeRhythmPoint": 2147483647,
                "headphone": 2147483647,
                "freeHeadphone": 2147483647,
                "dalcomCoin": 2147483647,
                "freeDalcomCoin": 2147483647
            }
        })

    # Respostas temporárias para avançarmos no teste inicial.
    if clazz in (
        "CardInventory",
        "CardBook",
        "LeagueWeekly",
        "StarLeague",
        "Game",
        "Attendance",
        "PostBox",
        "Mission",
        "Promotion",
        "Store"
    ):
        return ok([])

    print(
        "PROTOCOLO AINDA NÃO IMPLEMENTADO:",
        clazz,
        method,
        params,
        flush=True
    )

    return fail(
        -32601,
        {
            "error": "protocol_not_implemented",
            "class": clazz,
            "method": method
        }
    )


class Handler(BaseHTTPRequestHandler):

    server_version = "SSPA-Private-BIN/1.0"

    def log_message(self, fmt, *args):
        print(
            "HTTP",
            self.command,
            self.path,
            "-",
            fmt % args,
            flush=True
        )

    def send_json(self, obj, status=200):
        raw = json.dumps(
            obj,
            separators=(",", ":"),
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def send_binary(self, path):

        with open(path, "rb") as f:
            raw = f.read()

        print(
            "BIN:",
            os.path.basename(path),
            len(raw),
            "bytes",
            flush=True
        )

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/octet-stream"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.send_header(
            "Cache-Control",
            "no-cache"
        )
        self.end_headers()

        self.wfile.write(raw)

    def do_GET(self):

        parsed = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(parsed.path)

        if path in ("/", "/health"):
            self.send_json({
                "ok": True,
                "name": "SSPA Private Server BIN",
                "manifestVersion": MANIFEST_VERSION
            })
            return

        if "/version/" in path:
            manifest = (
                f"{PUBLIC_BASE_URL}/api,1,"
                f"{PUBLIC_BASE_URL}/rank,0,,,,,"
            )

            raw = manifest.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        # /assets/MusicData
        if path.startswith("/assets/"):

            requested = path[len("/assets/"):]

            # Nome lógico: MusicData, ThemeData etc.
            direct = asset_file(requested)

            if direct:
                self.send_binary(direct)
                return

            # Também aceita /assets/msd.bin
            basename = os.path.basename(requested)

            if basename in ASSET_MAP.values():
                candidate = os.path.join(ROOT, basename)

                if os.path.isfile(candidate):
                    self.send_binary(candidate)
                    return

            # Também aceita /assets/data/msd.bin
            if requested.startswith("data/"):
                basename = os.path.basename(requested)
                candidate = os.path.join(ROOT, basename)

                if (
                    basename in ASSET_MAP.values()
                    and os.path.isfile(candidate)
                ):
                    self.send_binary(candidate)
                    return

            print("BIN NÃO ENCONTRADO:", requested, flush=True)

            self.send_json({
                "code": 404,
                "result": None,
                "invoke": []
            }, 404)
            return

        if path.startswith("/rank"):
            self.send_json({})
            return

        if path in ("/api", "/api/"):
            self.send_json({
                "ok": True,
                "apiVersion": 8
            })
            return

        self.send_json({
            "code": 404,
            "result": None,
            "invoke": []
        }, 404)

    def do_POST(self):

        parsed = urllib.parse.urlsplit(self.path)

        if parsed.path not in ("/api", "/api/"):
            self.send_json(fail(404), 404)
            return

        length = int(
            self.headers.get("Content-Length", "0")
        )

        raw = self.rfile.read(length)

        try:

            # Algumas builds/testes enviam JSON diretamente.
            if raw.lstrip().startswith(b"{"):
                text = raw.decode("utf-8")

            else:
                iv = self.headers.get(
                    "X-SuperStar-AES-IV",
                    ""
                )

                text = decrypt_api(
                    raw,
                    iv
                ).decode("utf-8")

            req = json.loads(text)

            print(
                "REQUEST:",
                json.dumps(
                    req,
                    ensure_ascii=False,
                    separators=(",", ":")
                ),
                flush=True
            )

            response = handle_api(req)

            print(
                "RESPONSE:",
                json.dumps(
                    response,
                    ensure_ascii=False,
                    separators=(",", ":")
                ),
                flush=True
            )

            self.send_json(response)

        except Exception as e:

            print(
                "API ERROR:",
                repr(e),
                flush=True
            )

            self.send_json(
                fail(-32000, {"error": str(e)}),
                400
            )


if __name__ == "__main__":

    print()
    print("======================================")
    print(" SSPA Private Server - BIN TEST")
    print("======================================")
    print("API:", PUBLIC_BASE_URL + "/api")
    print("DATA:", ROOT)
    print()

    available = 0

    for logical, filename in ASSET_MAP.items():
        path = os.path.join(ROOT, filename)

        if os.path.isfile(path):
            available += 1
            print(
                "OK ",
                logical,
                "->",
                filename,
                "v" + str(asset_version(filename))
            )
        else:
            print(
                "FALTA",
                logical,
                "->",
                filename
            )

    print()
    print("Assets disponíveis:", available)
    print("Servidor bind:", f"http://{HOST}:{PORT}")
    print("URL pública configurada:", PUBLIC_BASE_URL)
    print()

    ThreadingHTTPServer(
        (HOST, PORT),
        Handler
    ).serve_forever()
