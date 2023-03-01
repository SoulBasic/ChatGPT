wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
tar -zxvf Python-3.7.0.tgz
cd Python-3.7.0
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel kernel-devel libffi-devel
./configure --with-ssl
yum -y install make gcc gcc-c++
yum -y install zlib*
yum install libffi-devel -y
make
make install
cd /usr/bin
rm python3
ln -s /usr/local/bin/python3.7 python3
python3 --version
