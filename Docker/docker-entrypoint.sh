#!/bin/bash

#echo "[google]" >> /etc/yum.repos.d/google.repo
#echo "name=Google-x86_64" >> /etc/yum.repos.d/google.repo
#echo "baseurl=http://dl.google.com/linux/rpm/stable/x86_64" >> /etc/yum.repos.d/google.repo
#echo "enabled=1" >> /etc/yum.repos.d/google.repo
#echo "gpgcheck=0" >> /etc/yum.repos.d/google.repo
#echo "gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub" >> /etc/yum.repos.d/google.repo


cd /home/JDMemberCloseAccount/driver
yum -y install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
cp ./chromedriver ../driver/chromedriver

sed -i 's/headless: false/headless: true/g' ./config.yaml
sed -i 's!binary: ""!binary: "/bin/google-chrome"!g' ./config.yaml

