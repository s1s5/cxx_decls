# -*- mode: dockerfile -*-
from opencv-base

ADD opencv /opt/source/opencv
ADD opencv_contrib /opt/source/opencv_contrib

RUN mkdir /opt/build/opencv
WORKDIR /opt/build/opencv
# RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_ZLIB=no -DBUILD_TIFF=no -DBUILD_JASPER=no -DBUILD_JPEG=no -DBUILD_PNG=no -DBUILD_OPENEXR=no -DWITH_JPEG=off -DWITH_PNG=off -DWITH_OPENEXR=off -DWITH_JASPER=off -DWITH_ZLIB=off -DWITH_TIFF=off -DWITH_WEBP=off -DWITH_HIGHGUI=off -DBUILD_opencv_highgui=off /opt/opencv
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DOPENCV_EXTRA_MODULES_PATH=/opt/source/opencv_contrib/modules /opt/source/opencv
RUN make -j 4
RUN make install

WORKDIR /work/
