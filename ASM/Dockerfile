FROM debian:bookworm

ARG USERNAME=ootr
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash

# Install build tools
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes curl gnupg ca-certificates \
  && curl https://practicerom.com/public/packages/debian/pgp.pub | apt-key add - \
  && echo deb http://practicerom.com/public/packages/debian staging main >/etc/apt/sources.list.d/practicerom.list \
  && apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes \
    build-essential \
    nodejs \
    npm \
    git \
    cmake \
    gdb-multiarch

# Install toolchain. Compile from source if not on Intel/AMD.
RUN if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes n64-ultra; \
  else \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes \
      wget \
      tar \
      make \
      diffutils \
      texinfo \
      gcc \
      g++ \
      lua5.3 \
      libjansson4 \
      libusb-1.0-0 \
      libgmp10 \
      liblua5.3-dev \
      libjansson-dev \
      libusb-1.0-0-dev \
      libgmp-dev \
      libmpfr-dev \
      zlib1g-dev; \
  fi
RUN if [ "$(dpkg --print-architecture)" != "amd64" ]; then \
    mkdir -p build \
    && cd build \
    && git clone --recursive https://github.com/glankk/n64.git \
    && cd n64 \
    && ./configure --enable-vc --prefix=/opt/n64 \
    && make install-toolchain \
    && make && make install \
    && make install-sys \
    && echo 'export PATH="/opt/n64/bin:$PATH"' >> /etc/profile; \
  fi

# Build armips
WORKDIR /build
RUN git clone --recursive https://github.com/Kingcom/armips.git
WORKDIR /build/armips
RUN mkdir build
WORKDIR /build/armips/build
RUN cmake -DCMAKE_BUILD_TYPE=Release .. \
  && cmake --build . \
  && mv ./armips /usr/local/bin/ \
  && chmod a+rx /usr/local/bin/armips

# Run as non-root user
USER $USERNAME
