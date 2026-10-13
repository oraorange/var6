"""Клиент RPC. Имена методов совпадают с методами модели."""
import json
import socket
from src.server import HOST, PORT, METHOD_CODES


class RPCClient:
    def __init__(self, host=HOST, port=PORT, timeout=5):
        self.host, self.port, self.timeout = host, port, timeout

    def _call(self, method, args=None):
        code = METHOD_CODES[method]
        body = json.dumps(args or {}, ensure_ascii=False).encode("utf-8")
        request = bytes([code]) + len(body).to_bytes(5, "little") + body
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(request)
            header = self._recv_exact(sock, 5)
            size = int.from_bytes(header[:4], "little")
            response_code = header[4]
            response = json.loads(self._recv_exact(sock, size).decode("utf-8"))
        if response_code != code:
            raise RuntimeError("Код операции в ответе не совпадает с запросом")
        if not response.get("ok"):
            raise RuntimeError(f'{response.get("error")}: {response.get("message")}')
        return response.get("result")

    @staticmethod
    def _recv_exact(sock, size):
        data = bytearray()
        while len(data) < size:
            part = sock.recv(size - len(data))
            if not part:
                raise ConnectionError("Сервер закрыл соединение")
            data.extend(part)
        return bytes(data)

    def create_member(self, values): return self._call("create_member", {"values": values})
    def delete_member(self, record_id): return self._call("delete_member", {"record_id": record_id})
    def get_all_members(self): return self._call("get_all_members")
    def edit_member(self, record_id, changes): return self._call("edit_member", {"record_id": record_id, "changes": changes})

    def create_prompt(self, values): return self._call("create_prompt", {"values": values})
    def delete_prompt(self, record_id): return self._call("delete_prompt", {"record_id": record_id})
    def get_all_prompts(self): return self._call("get_all_prompts")
    def edit_prompt(self, record_id, changes): return self._call("edit_prompt", {"record_id": record_id, "changes": changes})

    def create_response(self, values): return self._call("create_response", {"values": values})
    def delete_response(self, record_id): return self._call("delete_response", {"record_id": record_id})
    def get_all_responses(self): return self._call("get_all_responses")
    def edit_response(self, record_id, changes): return self._call("edit_response", {"record_id": record_id, "changes": changes})

    def query_recent_parameter_duration(self): return self._call("query_recent_parameter_duration")
