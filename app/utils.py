import torch
from functools import wraps

def custom_fwd(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        with torch.amp.custom_fwd(device_type='cuda'):
            return fn(*args, **kwargs)
    return wrapper 