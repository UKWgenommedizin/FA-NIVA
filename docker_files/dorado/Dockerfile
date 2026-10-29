FROM ontresearch/dorado:sha9809639e07a927bcc0f584dadd5e59674cf59f3f
LABEL description="Image with dorado and all models"
USER root
# Install essential packages
RUN mkdir -p /opt/dorado/models && \
    dorado download --models-directory /opt/dorado/models --model all

# Build requirements for HTSlib and samtools
RUN unset LD_LIBRARY_PATH && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bzip2 \
        build-essential \
        ca-certificates \
        libbz2-dev \
        libcurl4-openssl-dev \
        libdeflate-dev \
        liblzma-dev \
        libncurses-dev \
        libssl-dev \
        pkg-config \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

##############
#HTSlib 1.21#
##############
ENV HTSLIB_INSTALL_DIR=/opt/htslib

WORKDIR /tmp
RUN unset LD_LIBRARY_PATH && \
    wget https://github.com/samtools/htslib/releases/download/1.21/htslib-1.21.tar.bz2 && \
    tar --bzip2 -xvf htslib-1.21.tar.bz2 && \
    cd /tmp/htslib-1.21 && \
    ./configure  --enable-plugins --prefix=$HTSLIB_INSTALL_DIR && \
    make && \
    make install && \
    cp $HTSLIB_INSTALL_DIR/lib/libhts.so* /usr/lib/ && \
    cp $HTSLIB_INSTALL_DIR/bin/tabix /usr/local/bin/tabix && \
    cp $HTSLIB_INSTALL_DIR/bin/bgzip /usr/local/bin/bgzip && \
    rm -rf /tmp/htslib-1.21

################
#Samtools 1.21#
################
ENV SAMTOOLS_INSTALL_DIR=/opt/samtools

WORKDIR /tmp
RUN unset LD_LIBRARY_PATH && \
    wget https://github.com/samtools/samtools/releases/download/1.21/samtools-1.21.tar.bz2 && \
    tar --bzip2 -xf samtools-1.21.tar.bz2 && \
    cd /tmp/samtools-1.21 && \
    ./configure --with-htslib=$HTSLIB_INSTALL_DIR --prefix=$SAMTOOLS_INSTALL_DIR && \
    make && \
    make install && \
    ln -s /opt/samtools/bin/* /usr/local/bin/ && \
    cd / && \
    rm -rf /tmp/samtools-1.21

ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
