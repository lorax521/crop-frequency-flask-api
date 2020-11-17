from flask import request, Blueprint
from shapely.ops import transform, unary_union
from shapely.geometry import shape
import rasterio
from rasterio.mask import mask
import pyproj
import json
import os
import sys
import numpy as np
from time import time
from ..config import DBConfig

cropfrequency_blueprint = Blueprint('cropfrequency_blueprint', __name__)


@cropfrequency_blueprint.route('/cropfrequency', methods=['POST'])
def crop_frequency():
    """ Method: POST
        Visibility: public

        Analyzes the crop frequency planted between 2008 and 2019 in an area of interest, as defined by the request body GeoJSON.

        Response:
            crop_frequencies: dict -- a dictionary response (as json) containing the count of cells by crop frequency years. Schema: {data_source: {1_year: cell_count, 2_year: cell_count}}
    """
    t0 = time()
    if request.method == 'POST':
        try:
            dbConfig = DBConfig()
            db_path = dbConfig.DB_PATH

            def parse_request():
                """ Parses a GeoJSON request to shapely geometry. Includes error handling for feature collections, features, and feature geometry requestsdatetime A combination of a date and a time. Attributes: ()

                    Returns:
                        aoi: shapely geometry object -- Example: <shapely.geometry.polygon.Polygon object at 0x000002910AFE7D60>
                """
                try:
                    data = json.loads(request.data)
                    # parses feature collection
                    if 'features' in data.keys():
                        data = data['features']
                        # merges multi-feature feature collections into one geometry
                        if len(data) > 1:
                            features = [shape(feature['geometry'])
                                        for feature in data]
                            aoi = unary_union(features)
                            return aoi
                        else:
                            data = data[0]
                    # parses feature
                    if 'geometry' in data.keys():
                        data = data['geometry']
                    aoi = shape(data)
                    return aoi
                except:
                    print('Error - parseRequest: ' + sys.exc_info()[0])

            def reproject(shapely_geometry, from_crs, to_crs):
                """ Reprojects shapely geometry

                    Keyword Arguments:
                        shapely_geometry: shapley.geometry -- Point, LineString, or Polygon
                        from_crs: pyproj.CRS -- EPSG Authority projection (Example: pyproj.CRS('EPSG:4326'))
                        to_crs: pyproj.CRS -- EPSG Authority projection (Example: pyproj.CRS('EPSG:4269'))

                    Returns:
                        shapely_geometry_projected: shapley.geometry -- Point, LineString, or Polygon
                """
                # create projection transformation
                project = pyproj.Transformer.from_crs(
                    from_crs, to_crs, always_xy=True).transform
                # perform transform to new projection
                shapely_geometry_projected = transform(
                    project, shapely_geometry)
                return shapely_geometry_projected

            def zonal_statistics(value_raster, polygon_bounds):
                """ Calculates the count of each raster value in a polygon boundary

                    Keyword Arguments:
                        value_raster: rasterio raster -- Example: rasterio.open('raster.tif')
                        polygon_bounds: shapely.geometry.Polygon

                    Returns:
                        statistics: dict -- raster values as keys with counts as values
                """
                # mask the value_raster to the polygon_bounds
                try:
                    raster_mask, raster_mask_transform = mask(value_raster, [polygon_bounds], all_touched=False, crop=True)
                    # get unique keys
                    keys = [str(x) for x in np.unique(raster_mask)]
                    # count values for each key
                    values = [np.count_nonzero(
                        raster_mask == int(x)) for x in keys]
                    # add all keys and values to dict
                    statistics = dict(zip(keys, values))
                    return statistics
                except ValueError:
                    return {"nodata": 0}
                except:
                    print('Unexpected Error - zonal_statistics')

            def add_descriptive_statistics(crop_frequency_dict):
                """ Adds the sum and mean of dictionary values not including zero

                    Keyword Arguments/Returns:
                        crop_frequency_dict: dict -- a dictionary of crop frequencies by year
                """
                try:
                    crop_frequency_dict['sum'] = int(np.sum(
                        [crop_frequency_dict[x] * int(x) for x in crop_frequency_dict]))
                    crop_frequency_dict['mean'] = np.nan_to_num(crop_frequency_dict['sum'] / np.sum(
                        [int(v) for k, v in crop_frequency_dict.items() if k != '0' and k != 'sum']))
                    return crop_frequency_dict
                except ValueError:
                    return {"nodata": 0}
                except:
                    print('Unexpected Error - zonal_statistics')


            aoi = parse_request()  # request to shapely geometry

            crop_rasters = [x for x in os.listdir(db_path) if x.endswith(
                '.tif')]  # list crop raster datasets

            response = {}  # initialize dict to store zonal statistics
            # compute zonal statistics for each crop raster
            for crop_raster in crop_rasters:
                with rasterio.open(db_path + '/' + crop_raster) as raster:
                    # project aoi to raster EPSG
                    aoi_projected = reproject(
                        aoi, pyproj.CRS(dbConfig.REQUEST_EPSG), raster.crs)
                    # compute zonal statistics
                    crop_statistics = zonal_statistics(raster, aoi_projected)
                    # parse key name
                    key_name = raster.name.split(
                        '.tif')[0].split(db_path + '/')[1]
                    # calculate descriptive statistics
                    crop_statistics = add_descriptive_statistics(
                        crop_statistics)
                    # add crop statistics to response
                    response[key_name] = crop_statistics
            print('total elapsed time:' + str(time() - t0))
            return response
        except:
            raise Exception("Server error:" + str(sys.exc_info()[0]))
