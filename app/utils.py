import torch
from functools import wraps

def custom_fwd(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Для CPU используем обычный контекст без GPU-специфичных операций
        return fn(*args, **kwargs)
    return wrapper 