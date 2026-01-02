from typing import Any, Dict


def ok(data: Any = None, message: str = "ok") -> Dict[str, Any]:
    return {"code": "OK", "message": message, "data": data}
