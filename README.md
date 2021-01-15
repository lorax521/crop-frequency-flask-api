# Crop Frequency API

## Documentation

REST API to analyze crop frequencies as defined by the USDA's Cropland Data Layer (CDL). This API is built with Flask, Docker for containerization, and gunicorn for Web Server Gate Interface (WSGI).

### To Use

**Requirements**: 
- Install all Python requirements listed in the requirements.txt plus rasterio and gdal. 
- For production builds, docker is optional.
- Download crop frequency rasters (.tif) from the USDA at https://www.nass.usda.gov/Research_and_Science/Cropland/Release/ and place them in the root db directory (/db).

**Development**: 
- Windows: activate Python environment and run `python main.py`
- Unix: activate Python environment and run `python3 main.py`

**Production**:
- Unix: run a Web Server Gate Interface (WSGI) with `exec gunicorn --timeout 150 --workers 2 --threads 4 --bind 0.0.0.0:5000 wsgi:app` 
- For Docker deployment
  - Build the Docker image in the root directory: `docker build -t cropfrequency .`
  - Run in the Docker container: `docker run -d -p 8000:5000 cropfrequency`

### Routes

Route | Method | Visbility | Code Location
------|--------|-----------|--------------
/cropfrequency | POST | public | /app/blueprints/cropfrequency.py
<br/>
Description: Analyzes the crop frequency planted between 2008 and 2019 in an area of interest, as defined by the request body GeoJSON.
<br/>
<br/>
Request: GeoJSON polygon which defines the area of interest where the crop frequency statsitics are calculated.

Request Example:

```
  {
  "type": "Feature",
  "properties": {},
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [-86.10345363617176, 40.21040968097736],
        [-86.10010623932108, 40.21650528459179],
        [-86.08965635299879, 40.21042606774353],
        [-86.10345363617176, 40.21040968097736]
      ]
    ]
  }
```

Response: JSON containing the count of cells by crop frequency years, sum, and mean. Each key is the number of years planted and each value is number of cells for that year.

Response Example:

```
  {
    "corn": {
        "0": 568,
        "1": 2,
        "2": 1,
        "3": 15,
        "4": 64,
        "5": 151,
        "6": 70,
        "7": 104,
        "mean": 5.425061425061425,
        "sum": 2208
    },
    "cotton": {
        "0": 975,
        "mean": 0.0,
        "sum": 0
    },
    "soybeans": {
        "0": 566,
        "1": 2,
        "10": 1,
        "2": 2,
        "4": 2,
        "5": 107,
        "6": 70,
        "7": 152,
        "8": 61,
        "9": 12,
        "mean": 6.452322738386308,
        "sum": 2639
    },
    "wheat": {
        "0": 975,
        "mean": 0.0,
        "sum": 0
    }
}
```

## Background

Every year the USDA produces a Cropland Data Layer (CDL) which indicates coverage of crop types in the US. A derived product of the CDL is the National Frequency Layer, which indicates the number of times a crop type has been planted at a location over the past 12 years. This information is vital to farm management decision making due to soil degradation and disease/pest infestation that occurs when the same crop is planted year after year.

* *Subset National Frequency Layer*: http://nextcloud.beckshybrids.com/s/mcYnwm6nWxHtjMg (much smaller than full national dataset)
* *CDL & Derived Products*: https://www.nass.usda.gov/Research_and_Science/Cropland/Release/

## Project

As a farmer concerned with good crop rotation practices, I want a breakdown of crop type by number of years planted when planning upcoming planting for a single field so that I won't degrade the soil.

* Build an HTTP API to access crop frequency.
* Incoming requests will contain an arbitrary area of interest (AOI) geometry.

*Sample Request*
```
{
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          -86.10345363617176,
          40.21040968097736
        ],
        [
          -86.10010623932108,
          40.21650528459179
        ],
        [
          -86.08965635299879,
          40.21042606774353
        ],
        [
          -86.10345363617176,
          40.21040968097736
        ]
      ]
    ]
  }
}
```
