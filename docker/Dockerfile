from cxx_decls-base

ADD cxx /opt/source/cxx_decls_extractor
RUN mkdir -p /opt/build/cxx_decls_extractor
WORKDIR /opt/build/cxx_decls_extractor
RUN cmake /opt/source/cxx_decls_extractor
RUN make -j 4
RUN make install

ADD py /opt/source/cxx_decls_blueboss
WORKDIR /opt/source/cxx_decls_blueboss
RUN python setup.py install

RUN mkdir /work
WORKDIR /work

ADD docker/entrypoint.py /opt/
ENTRYPOINT ["python", "/opt/entrypoint.py"]
