FROM debian:bookworm

ARG USERNAME=ootr
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes curl gnupg ca-certificates \
  && curl https://practicerom.com/public/packages/debian/pgp.pub | apt-key add - \
  && echo deb http://practicerom.com/public/packages/debian staging main >/etc/apt/sources.list.d/practicerom.list \
  && apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends --assume-yes \
    build-essential \
    n64-ultra \
    nodejs \
    npm \
    git \
    cmake

WORKDIR /build
RUN git clone --recursive https://github.com/Kingcom/armips.git
WORKDIR /build/armips
RUN mkdir build
WORKDIR /build/armips/build
RUN cmake -DCMAKE_BUILD_TYPE=Release .. \
  && cmake --build . \
  && mv ./armips /usr/local/bin/ \
  && chmod a+rx /usr/local/bin/armips

USER $USERNAME
