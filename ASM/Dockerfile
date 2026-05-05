FROM debian:stable

ARG USERNAME=ootr
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash

# Install build tools
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes curl gnupg ca-certificates \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes \
    build-essential \
    nodejs \
    npm \
    git \
    cmake \
    gdb-multiarch \
    gpgv

# Install toolchain
RUN curl -o /usr/share/keyrings/practicerom-archive-keyring.gpg https://practicerom.com/public/packages/debian/practicerom-archive-keyring.gpg
RUN if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
    echo deb [arch=all,amd64 signed-by=/usr/share/keyrings/practicerom-archive-keyring.gpg] http://practicerom.com/public/packages/debian stable main > /etc/apt/sources.list.d/practicerom.list; \
  else \
    echo deb [arch=all,arm64 signed-by=/usr/share/keyrings/practicerom-archive-keyring.gpg] http://practicerom.com/public/packages/debian stable main > /etc/apt/sources.list.d/practicerom.list; \
  fi
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes practicerom-dev

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
