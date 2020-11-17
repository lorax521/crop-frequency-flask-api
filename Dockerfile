FROM continuumio/miniconda3

ADD wsgi.py .
ADD main.py .
ADD entrypoint.sh .
ADD requirements.txt .
ADD app app
ADD db db
RUN conda update conda
RUN conda config --add channels conda-forge
RUN conda install -y -c conda-forge gdal rasterio
RUN conda install --file requirements.txt

EXPOSE 5000

# development container
# ENTRYPOINT ["python", "main.py"]

# production container
ENTRYPOINT ["sh", "entrypoint.sh"]