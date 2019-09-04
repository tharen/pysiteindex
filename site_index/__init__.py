
from . import si

# Enumerate site curve subclasses
curves = {c.__curve_name__:c for c in si.SiteCurve.__subclasses__()}
