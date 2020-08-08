import warnings

try:
    import apsw
except ImportError as e:
    warnings.warn(
        "praxis-bot requires apsw as a dependency for SQLite 3 database "
        "management. apsw is not available on PyPi and must be downloaded and "
        "installed using the instructions described on their website: "
        "https://rogerbinns.github.io/apsw/download.html and "
        "https://rogerbinns.github.io/apsw/build.html"
    )
