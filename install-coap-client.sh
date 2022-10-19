#!/bin/sh

if [ $(id -u) -ne 0 ]
  then echo "Please run the script as: sudo ./install-coap-client.sh"
  exit
fi

apt-get install -f autoconf automake libtool  

echo "***Running 'libcoap' cloning...***"
git clone --depth 1 --recursive -b dtls https://github.com/home-assistant/libcoap.git
cd libcoap
echo "***Running autogen install...***"
./autogen.sh
echo "***Running configure...***"
./configure --disable-documentation --disable-shared --without-debug CFLAGS="-D COAP_DEBUG_FD=stderr"
make
make install