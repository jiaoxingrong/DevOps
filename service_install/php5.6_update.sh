#!/bin/bash -
#php5.6 update
InstallPath='/application/php5.6.16'

function php_bulid() {
    RAM=`egrep MemTotal /proc/meminfo  |awk '{print int($2/1024)}'`
    DownUrl='http://package.brotlab.net:8086/package/bulid_php'
    ConfUrl='http://package.brotlab.net:8086/package/init'
    PHP_Pack='php-5.6.16.tar.gz'

    #判断是否为EC2,来确认php-fpm运行用户
    run_user='ec2-user'
    id ${run_user} || useradd ${run_user} -s /sbin/nologin
    #判断cpu核心数
    cpu_num=`cat /proc/cpuinfo |grep "processor"|wc -l`
    curr_path=`pwd`
    #安装依赖包
    yum -y --skip-broken install libjpeg-devel libpng-devel freetype-devel aspell-devel libXpm-devel gettext-devel gmp-devel openldap-devel readline-devel libxslt-devel perl-DBI perl-DBD-Pg autoconf libjpeg libpng freetype libxml2 libxml2-devel zlib* glibc glibc-devel glib2 glib2-devel bzip2 bzip2-devel ncurses ncurses-devel curl curl-devel e2fsprogs e2fsprogs-devel krb5 krb5-devel libidn libidn-devel openssl openssl-devel openldap openldap-devel nss_ldap openldap-clients openldap-servers gcc* libxml* sysstat libjpeg-devel aspell-devel libtiff-devel libXpm-devel gettext-devel gmp-devel openldap-devel readline-devel apr vim* libgearman libgearman-devel libxslt-devel expect libtool ntp vim-enhanced flex bison  automake ncurses-devel libXpm-devel gettext-devel pam-devel kernel libtool-ltdl-devel* pcre-devel bc libaio openssh-clients geoip geoip-devel jemalloc-devel libmcrypt-devel libmemcached libmemcached-devel postgresql-devel icu libicu libicu-devel wget git
   [[ -e '/usr/local/lib64' ]] && echo '/usr/local/lib64' >> /etc/ld.so.conf
    echo -e '/usr/local/lib' >> /etc/ld.so.conf
    ln -s /usr/lib64/libssl.so /usr/lib/
    ldconfig

    #CentOS 使用yum无法安装libmcrypt，进行源码编译安装。
    wget -q ${DownUrl}/libmcrypt-2.5.7.tar.gz
    tar xf libmcrypt-2.5.7.tar.gz
    cd libmcrypt-2.5.7
    ./configure
    make -j${cpu_num}
    make install
    cd ${curr_path}
    rm -fr libmcrypt-2.5.7

    #下载libmemcached扩展(使用yum安装没有开始sasl支持)和php5.6源码包，并编译安装。
    wget -q ${DownUrl}/${PHP_Pack} ${DownUrl}/libmemcached-1.0.18.tar.gz
    tar xf libmemcached-1.0.18.tar.gz
    cd libmemcached-1.0.18

    #测试中CentOS 5.x 有些系统会编译失败，使用gcc44可以解决，如果失败，才会执行。
    grep 'CentOS release 5.*' /etc/issue
    if [[ $? -eq 0 ]]; then
        # 使用gcc44来作为编译器
        export CC="gcc44"
        export CXX="g++44"
        ./configure
        make -j${cpu_num}
        make install
        unset CC CXX
    else
        ./configure
        make -j${cpu_num}
        make install
    fi
    cd ${curr_path}
    rm -fr libmemcached-1.0.18

    #编译安装php5.6
    [[ -e ${InstallPath} ]] && rm -fr ${InstallPath}
    mkdir -p ${InstallPath}
    tar xf ${PHP_Pack}
    php_name=`echo ${PHP_Pack} |sed 's/.tar.gz//'`
    cd ${php_name}
    './configure'  "--prefix=${InstallPath}" "--with-config-file-path=${InstallPath}/etc" '--enable-fpm' '--with-fpm-user=www' '--with-fpm-group=www' '--with-mysql=mysqlnd' '--with-mysqli=mysqlnd' '--with-pdo-mysql=mysqlnd' '--with-iconv-dir' '--with-freetype-dir' '--with-jpeg-dir' '--with-png-dir' '--with-zlib' '--with-libxml-dir' '--enable-xml' '--disable-rpath' '--enable-bcmath' '--enable-shmop' '--enable-sysvsem' '--enable-inline-optimization' '--with-curl' '--enable-mbregex' '--enable-mbstring' '--with-mcrypt' '--enable-ftp' '--with-gd' '--enable-gd-native-ttf' '--with-openssl' '--with-mhash' '--enable-pcntl' '--enable-sockets' '--with-xmlrpc' '--enable-zip' '--enable-soap' '--with-gettext' '--enable-sysvshm' '--with-pdo-pgsql' '--enable-sysvmsg' '--with-bz2' '--with-pgsql' '--with-gmp'

    make -j${cpu_num} ||  make -j${cpu_num} ZEND_EXTRA_LIBS='-liconv'
    make install
    cd ${curr_path}
    rm -fr ${php_name}

    #下载php-fpm.conf及php.ini
    wget -q -P ${InstallPath}/etc/ ${ConfUrl}/php-fpm.conf.tpl ${ConfUrl}/php5.6.ini.tpl
    #修改php-fpm运行用户
    sed -i "s/@USER@/$run_user/g" ${InstallPath}/etc/php-fpm.conf.tpl
    php_child=$(($RAM/15))
    sed -i "s/@CHILD@/$php_child/g" ${InstallPath}/etc/php-fpm.conf.tpl
    sed -i "s/127.0.0.1:9000/127.0.0.1:9009/" ${InstallPath}/etc/php-fpm.conf.tpl
    sed -i "s#/application/php/#${InstallPath}/#" ${InstallPath}/etc/php-fpm.conf.tpl
    #修改php扩展路径
    sed -i "/^extension_dir/cextension_dir='${InstallPath}/lib/php/extensions/no-debug-non-zts-20131226/'" ${InstallPath}/etc/php5.6.ini.tpl
    #改名
    mv ${InstallPath}/etc/php-fpm.conf.tpl ${InstallPath}/etc/php-fpm.conf
    mv ${InstallPath}/etc/php5.6.ini.tpl ${InstallPath}/etc/php.ini
    #使用pecl安装memcached，igbinary,redis扩展
    ${InstallPath}/bin/pecl  install  igbinary memcache memcached
    #安装composer
    ${InstallPath}/bin/php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
    ${InstallPath}/bin/php 'composer-setup.php' --install-dir=${InstallPath}/bin --filename=composer
    ${InstallPath}/bin/php -r "unlink('composer-setup.php');" 2&1 > /dev/null
    #判断当前路径及/etc/init.d/有没有php-fpm5.6的文件，下载php启动文件到/etc/init.d/
    [[ -e ./php-fpm5.6 ]] && rm -f php-fpm5.6
    [[ -e /etc/init.d/php-fpm5.6 ]] && mv /etc/init.d/php-fpm5.6{,_old}
    wget -q -O php-fpm5.6 ${ConfUrl}/php-fpm && mv php-fpm5.6 /etc/init.d/
    sed -i "s#/application/php#${InstallPath}#" /etc/init.d/php-fpm5.6
    chmod +x /etc/init.d/php-fpm5.6
    mkdir -p /data/logs/
    chmod 777 /data/logs
    /etc/init.d/php-fpm5.6 start
}

function php_install() {
    read  -p '确认升级，将停止当前php服务。'

    #找出当前环境变量中的php命令
    php_path=`which php`
    phpize_path=`which phpize`
    phpconfig_path=`which php-config`
    pecl_path=`which pecl`
    composer_path=`which composer`

    #删除旧的php命令
    [[ -e ${php_path} ]] && rm -f ${php_path}
    [[ -e ${phpize_path} ]] && rm -f ${phpize_path}
    [[ -e ${phpconfig_path} ]] && rm -f ${phpconfig_path}
    [[ -e ${pecl_path} ]] && rm -f ${pecl_path}

    #停止旧的php-fpm并重命名旧的init文件和程序文件夹
    [[ -e /etc/init.d/php-fpm ]] && /etc/init.d/php-fpm stop && mv /etc/init.d/php-fpm{,_old}
    [[ -e '/application/php' ]] && mv /application/php{,_old}

    #将php5.6安装目录链接为/application/php
    ln -s ${InstallPath} /application/php

    #将新的php命令链接到/usr/local/bin下
    ln -s /application/php/bin/php /usr/local/bin/
    ln -s /application/php/bin/phpize /usr/local/bin/
    ln -s /application/php/bin/php-config /usr/local/bin/
    ln -s /application/php/bin/pecl /usr/local/bin/
    ln -s /application/php/bin/composer /usr/local/bin/

    #将新的init文件重命名为/etc/init.d/php-fpm
    mv /etc/init.d/php-fpm5.6 /etc/init.d/php-fpm
    #更改端口为9000
    sed -i 's/127.0.0.1:9009/127.0.0.1:9000/' ${InstallPath}/etc/php-fpm.conf

    /etc/init.d/php-fpm restart
}

function roolback(){
    read -p '确认回退，将停止当前php服务。'

    /etc/init.d/php-fpm stop

    #找出当前环境变量中的php命令
    php_path=`which php`
    phpize_path=`which phpize`
    phpconfig_path=`which php-config`
    pecl_path=`which pecl`
    composer_path=`which composer`

    #删除旧的php命令
    [[ -e ${php_path} ]] && rm -f ${php_path}
    [[ -e ${phpize_path} ]] && rm -f ${phpize_path}
    [[ -e ${phpconfig_path} ]] && rm -f ${phpconfig_path}
    [[ -e ${pecl_path} ]] && rm -f ${pecl_path}

    #取消/application/php旧的程序文件夹链接
    unlink /application/php

    #将旧的PHP文件夹重命名为php_current,将当前的php文件夹命名为php_old
    mv /application/php_old /application/php_current
    mv ${InstallPath} /application/php_old

    ln -s /application/php_current /application/php

    #将新的php命令链接到/usr/local/bin下
    ln -s /application/php/bin/php /usr/local/bin/
    ln -s /application/php/bin/phpize /usr/local/bin/
    ln -s /application/php/bin/php-config /usr/local/bin/
    ln -s /application/php/bin/pecl /usr/local/bin/
    ln -s /application/php/bin/composer /usr/local/bin/

    #重启php-fpm
    /etc/init.d/php-fpm start
}

read -p '
    1. 预配置运行在9009端口的php5.6
    2. 升级替换当前运行的php
    3. 退回到安装之前的php版本
' num

case $num in
    1 )
       echo | php_bulid ;;
    2 )
       php_install ;;
    3 )
        roolback ;;
esac

