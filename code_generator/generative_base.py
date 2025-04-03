from .universal_attribute import UniversalAttribute

class GenerativeBase:
    def __getattr__(self, name):
        print(f"GenerativeBase: __getattr__ called for {name}")
        return UniversalAttribute(name, self)


