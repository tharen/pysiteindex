# pysiteindex
A Python package for exploring and using forest height growth
and site index functions.

## PySiteIndex CLI

PySiteIndex provides a basic command line interface to
perform site index and height estimation for single
trees.

### Usage

```
$ pysi --help
Usage: pysi [OPTIONS] COMMAND [ARGS]...

Options:
  --help-curves  Return a list of supported site curve funtions.
  --help         Show this message and exit.

Commands:
  ht  Return the estimated height of a single tree for a given age and...
  si  Return the site index estimate for a single tree.

  ```

### List Available Curves

```
$ pysi help-curves
Site Index Curves:
  bruce_1981: Douglas-fir, Bruce (1981)
  curtis_1974: Douglas-fir, Curtis, 1972
  farr_1984: Sitka spruce, Farr (1984), Res. Paper PNW-326
  fvs: Species site curves embedded in FVS variant libraries.
  harrington_1986: Red alder, Harrington (1986)
  king_1966: Douglas-fir, King (1966)
  wiley_1978: Western Hemlock, FIA PNW eq. 5a, Wiley (1978)
```

### Estimate Site Index

```
$ pysi si --help
Usage: pysi si [OPTIONS]

  Return the site index estimate for a single tree.

Options:
  -c, --curve TEXT      Site curve name.  [required]
  -a, --age FLOAT       Tree age - BHA, TTA, etc. see curve description.
                        [required]
  -t, --height FLOAT    Tree height - See curve description.  [required]
  -v, --variant TEXT    FVS variant abbreviation when curve="fvs".
  -f, --forest INTEGER  FVS forest code when curve="fvs".
  -s, --species TEXT    FVS species code when curve="fvs".
  --help                Show this message and exit.
```
```
$ pysi si --curve=bruce_1981 --age=43 --height=107
118.28ft @bha=50
```

### Estimate Height

```
$ pysi ht --help
Usage: pysi ht [OPTIONS]

  Return the estimated height of a single tree for a given age and site index.

Options:
  -c, --curve TEXT        Site curve name.  [required]
  -a, --age FLOAT         Tree age - BHA, TTA, etc. see curve description.
                          [required]
  -i, --site-index FLOAT  Site index - See curve description.  [required]
  -v, --variant TEXT      FVS variant abbreviation when curve="fvs".
  -f, --forest INTEGER    FVS forest code when curve="fvs".
  -s, --species TEXT      FVS species code when curve="fvs".
  --help                  Show this message and exit.
```
```
$ pysi ht --curve=bruce_1981 --age=97 --site-index=107
152.17ft @bha=97.0
```

### FVS Site Curves

If the PyFVS package is available PySiteIndex can estimate site index and heights for any tree species from a variants of the Forest Vegetation Simulator (more can be added).

Sugar pine, Inland CA and S. Cascades variant
```
$ pysi si -c FVS -v CA -s SP -a 76 -t 124
87.21ft @bha=50
```

Pacific Yew, PN variant
```
$ pysi si -c FVS -v PN -s PY -a 43 -t 32
61.43ft @bha=100
```

## PySiteIndex API

### Basic usage
Estimate site index
```python
from pysiteindex import si as pysi

sc = pysi.DF_Bruce_SiteCurve()

# Estimate site index from breast-height age and total height
si = sc.site_index(bha=75, ht=145)
print(si)
114.8828125

# Also accepts iterables and numpy arrays
si = sc.site_index(bha=[45,75], ht=[110,145])
print(si)
[117.8125    114.8828125]
```

Estimate height
```python
ht = sc.height(bha=120, si=130)
print(ht)
205.97416666910453
```

Estimate breast height age
```python
age = sc.age(ht=95, si=120)
print(age)
35.60888671875
```

### Plot Site Index Curves

Standard Height Curves

```python
import matplotlib.pyplot as plt
from pysiteindex import si as pysi

sc = pysi.DF_Bruce_SiteCurve()
fig,ax = plt.subplots()

ax = sc.plot_height_curves(min_bha=0, min_si=90, max_si=150, ax=ax)
```
![Height Curves](/doc/img/height_curves_df_bruce.png)

Height Growth Curves

```python
import matplotlib.pyplot as plt
from pysiteindex import si as pysi

sc = pysi.DF_Bruce_SiteCurve()
fig,ax = plt.subplots()

ax = sc.plot_height_growth(min_bha=0, min_si=90, max_si=150, ax=ax)
```
![Height Curves](/doc/img/height_growth_curves_df_bruce.png)

Site Index Curves
```python
import matplotlib.pyplot as plt
from pysiteindex import si as pysi

sc = pysi.DF_Bruce_SiteCurve()
fig,ax = plt.subplots()

ax = sc.plot_site_index_curves(ax=ax)
```
![Site Index Curves](/doc/img/site_index_curves_df_bruce.png)