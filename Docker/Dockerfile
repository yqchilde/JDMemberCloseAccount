FROM centos:7
ENV container docker
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]

RUN set -x \
	&& yum -y install wget libXdamage libXcomposite libXrandr  mesa-libGL.x86_64 atk nss at-spi2-atk cups-libs mesa-libgbm alsa-lib git \
	&& yum -y install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel gcc make yum-utils unzip \
	&& cd ~/ \
	&& mkdir python \
	&& cd python  \
	&& wget https://mirrors.huaweicloud.com/python/3.7.7/Python-3.7.7.tgz  \
	&& tar -xvf Python-3.7.7.tgz \
	&& rm Python-3.7.7.tgz \
	&& cd Python-3.7.7 \
	&& ./configure --prefix=/usr/local/python3 \
	&& make \
	&& make install \
	&& cd .. \
	&& rm -rf Python-3.7.7 \
	&& echo "export PATH=\$PATH:/usr/local/python3/bin">>/etc/profile \
	&& source /etc/profile \
	&& ln -sf /usr/local/python3/bin/python3.7 /bin/python3 \
	&& ln -sf /usr/local/python3/bin/pip3 /bin/pip3 \
	&& pip3 install --upgrade pip \
	&& pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple selenium psutil func_timeout requests urllib3 pillow websockets numpy pyyaml opencv-python schedule\
	&& cd /home/ \
	&& git clone https://gitee.com/xxsc/JDMemberCloseAccount.git \
	&& cd JDMemberCloseAccount \
	&& chmod +x mykill.sh \
	&& ln -sf /home/JDMemberCloseAccount/mykill.sh /bin/mykill \
	&& sed -i 's!headless: false!headless: true!g' ./config.yaml \
	&& sed -i 's!binary: ""!binary: "/bin/google-chrome"!g' ./config.yaml \
	&& sed -i 's!type: "yolov4"!type: "local"!g' ./config.yaml \
	&& cd Docker \
	&& yum -y install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm \
	&& cp chromedriver ../drivers/chromedriver \
	&& cd ../drivers \
	&& chmod +x chromedriver