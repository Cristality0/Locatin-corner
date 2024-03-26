from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


def get_labeled_exif(file) -> Dict[str, Any]:
    """Get EXIF data as a human readable dict."""
    with Image.open(file) as image:
        image.verify()
        exif = image._getexif()  # noqa
    return {TAGS.get(key, key): value for key, value in exif.items() if key in TAGS}


def get_gps_info(exif_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get GPS Info data as a human readable dict."""
    return {GPSTAGS.get(key, key): value for key, value in exif_data.get("GPSInfo", {}).items() if key in GPSTAGS}


def _get_gps_coord(coord_name: str, gps_info: Dict[str, Any]) -> Optional[float]:
    """Get and convert GPS Info coordinates."""
    coord_key = f"GPS{coord_name.capitalize()}"
    coord_value = gps_info.get(coord_key)
    if coord_value is None:
        return None

    d, m, s = coord_value
    # Convert IFDRational values to Decimal
    d_dec = Decimal(d.numerator) / Decimal(d.denominator)
    m_dec = Decimal(m.numerator) / Decimal(m.denominator)
    s_dec = Decimal(s.numerator) / Decimal(s.denominator)

    decimal_degrees = d_dec + m_dec / Decimal(60) + s_dec / Decimal(3600)

    coord_ref_key = f"{coord_key}Ref"
    if gps_info.get(coord_ref_key) in {"S", "W"}:
        decimal_degrees *= -1

    return round(float(decimal_degrees), ndigits=7)


def _get_altitude(exif_geo: Dict[str, Any]) -> Optional[float]:
    altitude = exif_geo.get("GPSAltitude")
    if altitude is None:
        return None

    if exif_geo.get("GPSAltitudeRef") == 1:
        altitude *= -1

    return altitude


def get_datetime(exif_data: Dict[str, Any]) -> Optional[datetime]:
    return datetime.strptime(exif_data.get("DateTimeOriginal", ""),
                             "%Y:%m:%d %H:%M:%S")


def get_location(exif_data: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Returns the latitude, longitude, datetime, and altitude, if available
    """
    gps_info = get_gps_info(exif_data)
    location = {
        "latitude": _get_gps_coord("Latitude", gps_info),
        "longitude": _get_gps_coord("Longitude", gps_info),
        "altitude": _get_altitude(gps_info),
        "datetime": get_datetime(exif_data),
    }
    return {k: v for k, v in location.items() if v is not None}


def img2location(img_path: str) -> Dict[str, Optional[float]]:
    exif_data = get_labeled_exif(img_path)
    return get_location(exif_data)

# test
