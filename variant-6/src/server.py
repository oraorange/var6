"""TCP RPC-сервер по формату задания: запрос [код:1][длина:5][JSON], ответ [длина:4][код:1][JSON]."""
import json
import logging
import socket
import threading
from src.model import DataModel

HOST = "127.0.0.1"
PORT = 5055
OPS = {
    1: "create_member", 2: "delete_member", 3: "get_all_members", 4: "edit_member",
    5: "create_prompt", 6: "delete_prompt", 7: "get_all_prompts", 8: "edit_prompt",
    9: "create_response", 10: "delete_response", 11: "get_all_responses", 12: "edit_response",
    13: "query_recent_parameter_duration",
}
METHOD_CODES = {name: code for code, name in OPS.items()}
logging.basicConfig(filename="journal.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


def recv_exact(sock, size):
    chunks = []
    remaining = size
    while remaining:
        part = sock.recv(remaining)
        if not part:
            raise ConnectionError("Соединение закрыто до получения полного сообщения")
        chunks.append(part)
        remaining -= len(part)
    return b"".join(chunks)


def dispatch(model, method, args):
    fn = getattr(model, method)
    if method in ("create_member", "create_prompt", "create_response"):
        return fn(args.get("values", {}))
    if method in ("delete_member", "delete_prompt", "delete_response"):
        return fn(args["record_id"])
    if method in ("edit_member", "edit_prompt", "edit_response"):
        return fn(args["record_id"], args.get("changes", {}))
    return fn()


def handle_client(conn, model):
    with conn:
        while True:
            try:
                header = conn.recv(6)
                if not header:
                    return
                while len(header) < 6:
                    header += recv_exact(conn, 6 - len(header))
                code = header[0]
                body_size = int.from_bytes(header[1:6], "little")
                body_raw = recv_exact(conn, body_size)
                logging.info("REQUEST code=%s body=%s", code, body_raw.decode("utf-8", "replace"))
                try:
                    if code not in OPS:
                        raise ValueError(f"Неизвестный код операции: {code}")
                    args = json.loads(body_raw.decode("utf-8")) if body_raw else {}
                    result = dispatch(model, OPS[code], args)
                    payload = {"ok": True, "result": result}
                except Exception as exc:
                    payload = {"ok": False, "error": type(exc).__name__, "message": str(exc)}
                response_body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
                response = len(response_body).to_bytes(4, "little") + bytes([code]) + response_body
                logging.info("RESPONSE code=%s body=%s", code, response_body.decode("utf-8"))
                conn.sendall(response)
            except (ConnectionError, OSError):
                return


def serve(host=HOST, port=PORT, model=None):
    model = model or DataModel()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f"RPC-сервер запущен: {host}:{port}. Для остановки нажми Ctrl+C.")
    try:
        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle_client, args=(conn, model), daemon=True).start()
    finally:
        server.close()


if __name__ == "__main__":
    serve()
