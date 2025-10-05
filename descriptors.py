class BoundedStat:
    def __init__(self, name: str, minimum: int = 0, maximum_attr: str | None = None):
        self.private_name = f"_{name}"; self.minimum = minimum; self.maximum_attr = maximum_attr
    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return getattr(obj, self.private_name, 0)
    def __set__(self, obj, value):
        v = int(value); max_v = getattr(obj, self.maximum_attr, None) if self.maximum_attr else None
        if max_v is not None: v = min(v, max_v)
        v = max(v, self.minimum)
        setattr(obj, self.private_name, v)