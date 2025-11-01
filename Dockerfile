FROM ubuntu:20.04

LABEL maintainer="OpenBMC CI/CD Lab"
LABEL description="Local build of OpenBMC QEMU environment"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    qemu-system-x86 \
    curl \
    net-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/openbmc

RUN curl -L -o openbmc.qcow2 https://jenkins.openbmc.org/job/latest-master-romulus/lastSuccessfulBuild/artifact/openbmc/build/romulus/deploy/images/obmc-phosphor-image-romulus.qcow2

EXPOSE 2222 2443

CMD ["qemu-system-x86_64", \
    "-m", "1024", \
    "-machine", "romulus-bmc", \
    "-drive", "file=/opt/openbmc/openbmc.qcow2,format=qcow2,if=mtd", \
    "-nographic", \
    "-netdev", "user,id=net0,hostfwd=tcp::2222-:22,hostfwd=tcp::2443-:443", \

    "-device", "net-virtio,netdev=net0"]
