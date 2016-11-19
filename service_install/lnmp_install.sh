#!/bin/bash -

basedir='/application'
RAM2=`egrep MemTotal /proc/meminfo  |awk '{print int($2/1024/2)}'`
# wnic=(`route -n | awk '{if($1~"^0.0.0.0")print $NF}' | tr '\n' ' '`)
# lnic=`route -n | awk '{print $NF}' |grep -E "eth|bond|em" | sort -u |egrep -v "$wnic"`
user='ec2-user'
id ${user} 2>1 >/dev/null || useradd ${user}

# if [ -z $lnic ]; then
#     ipin=`ifconfig $wnic | grep "inet addr:" | awk '{print $2}' | awk -F: '{print $2}'`
# else
#     ipin=`ifconfig $lnic | grep "inet addr:" | awk '{print $2}' | awk -F: '{print $2}'`
# fi

cpucount=`cat /proc/cpuinfo |grep "processor"|wc -l`
#cpucount2=`echo "2 * $cpucount" | bc`
cpucount2=`echo $((2*$cpucount))`
[[ -e /etc/sysconfig/selinux ]] && sed -i 's/SELINUX=.*/SELINUX=disabled/'
setenforce 0

#判断是否内网
read -p '    是否为内网环境安装(回车否)[y/n]: ' if_lan
case ${if_lan} in
    y|Y|yes|YES )
        packdownurl="http://10.1.9.200:8086/package/"
        initurl="http://10.1.9.200:8086/init/"
        ;;
    * )
        DownUrl="http://d1aegnnxokxfi0.cloudfront.net"
        packdownurl="http://d1aegnnxokxfi0.cloudfront.net/package/"
        initurl="http://d1aegnnxokxfi0.cloudfront.net/package/init/"
        ;;
esac

#Nginx、php、mysql下载包名
if `grep "CentOS release 5.* (Final)" /etc/issue >/dev/null`;then
    phppackname="php_el5.tgz"
fi

nginxpackname='tengine-2.1.2.tar.gz'
nginxconfname="nginx.conf.tpl"
nginxinitname="nginx"
phpinitname="php-fpm"
phpconfname="php-fpm.conf.tpl"
mysqlpackname="mysql-5.6.17.tgz"
mysqlconfname="my.cnf.tpl"
mysqlinitname="mysqld"

#php版本选择
function php_ver_choose() {
    read -p '
    1. 5.6
    2. 5.5
    3. 5.3
    请输入要安装的php版本(默认5.6【5.3版本仅支持6.x的系统】): ' php_num
    case ${php_num} in
        1 )
            phppackname=6
            ;;
        2 )
            phppackname="php_el6.tgz"
            ;;
        3 )
            phppackname="php5.3_el6.tgz"
            ;;
        * )
            phppackname=6
            ;;
    esac
}

#优化系统参数及配置
function basic_parse_optimize() {
    ls /etc/CHECKOAS/checkdir/checkfile &>/dev/null && return
    read -p "输入想要设置的主机名(回车不设置): " USERHOSTNAME
    if [ ! -z $USERHOSTNAME ]; then
        sed -i "s/HOSTNAME=.*/HOSTNAME=$USERHOSTNAME/" /etc/sysconfig/network
        hostname $USERHOSTNAME
    fi

    rpm -qa |grep ntpdate || yum install ntpdate -y
    /etc/init.d/ntpd stop &>/dev/null
    ntpdate 1.centos.pool.ntp.org || exit 1
    /etc/init.d/ntpd start
    chkconfig ntpd on

    modprobe bridge
    modprobe nf_conntrack
    echo "modprobe bridge">> /etc/rc.local
    echo "modprobe nf_conntrack">> /etc/rc.local
    echo 'export PS1="\[\033[01;31m\]\u\[\033[0;37m\]@\[\033[32m\]\H.$add \[\033[0;33m\]\w\[\033[0;36m\]\\$ \[\033[37m\]"' >> /etc/profile
    source /etc/profile
cat >>/etc/rc.local<<EOF
ulimit -SHn 655350
EOF
   ulimit -SHn 655350

cat >>/etc/security/limits.conf<<EOF
*           soft   nofile       65535
*           hard   nofile       65535
EOF

cat >>/etc/sysctl.conf<<EOF
net.ipv4.tcp_fin_timeout = 2
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_keepalive_time =600
net.ipv4.ip_local_port_range = 4000    65000
net.ipv4.tcp_max_syn_backlog = 16384
net.ipv4.tcp_max_tw_buckets = 36000
net.ipv4.route.gc_timeout = 100
net.ipv4.tcp_syn_retries = 1
net.ipv4.tcp_synack_retries = 1
net.core.somaxconn = 16384
net.core.netdev_max_backlog = 16384
net.ipv4.tcp_max_orphans = 16384
net.nf_conntrack_max = 25000000
net.netfilter.nf_conntrack_max = 25000000
net.netfilter.nf_conntrack_tcp_timeout_established = 180
net.netfilter.nf_conntrack_tcp_timeout_time_wait = 120
net.netfilter.nf_conntrack_tcp_timeout_close_wait = 60
net.netfilter.nf_conntrack_tcp_timeout_fin_wait = 120
EOF
    sysctl -p
    mkdir -p /etc/CHECKOAS/checkdir && echo "This is an scripts check file ,don't delete!" > /etc/CHECKOAS/checkdir/checkfile
}

function init_yum_install() {
    yum clean all
    yum install epel-release -y
    sed -i 's/https/http/'  /etc/yum.repos.d/epel.repo
    yum -y --skip-broken install libjpeg-devel libpng-devel freetype-devel aspell-devel libXpm-devel gettext-devel gmp-devel openldap-devel readline-devel libxslt-devel perl-DBI perl-DBD-Pg autoconf libjpeg libpng freetype libxml2 libxml2-devel zlib* glibc glibc-devel glib2 glib2-devel bzip2 bzip2-devel ncurses ncurses-devel curl curl-devel e2fsprogs e2fsprogs-devel krb5 krb5-devel libidn libidn-devel openssl openssl-devel openldap openldap-devel nss_ldap openldap-clients openldap-servers gcc* libxml* sysstat libjpeg-devel aspell-devel libtiff-devel libXpm-devel gettext-devel gmp-devel openldap-devel readline-devel apr vim* libgearman libgearman-devel libxslt-devel expect libtool ntp vim-enhanced flex bison  automake ncurses-devel libXpm-devel gettext-devel pam-devel kernel libtool-ltdl-devel* pcre-devel bc libaio openssh-clients geoip geoip-devel jemalloc-devel libmcrypt-devel libmemcached libmemcached-devel postgresql-devel icu libicu libicu-devel wget git
}

function iptables_install() {
grep -q "Amazon Linux" /etc/issue
if [ $? -ne 0 ]; then
    ls /root/init_iptables.sh &>/dev/null && mv /root/init_iptables.sh /root/init_iptables.sh.bak
    mkdir -p /data/scripts
    wget -q -P /data/scripts $DownUrl/iptables.sh
    chmod +x /data/scripts/iptables.sh
    sh /data/scripts/iptables.sh
    chkconfig iptables on
    service iptables save
fi
}

function nginx_install() {
    mkdir -p /application/ /data/logs /data/htdocs
    chmod 777 /data/logs
    rpm -qa |grep wget &>/dev/null|| yum install wget -y &>/dev/null
    wget $packdownurl$nginxpackname  $initurl$nginxinitname $initurl$nginxconfname >/dev/null
    tar xf $nginxpackname -C $basedir &&  rm -f $nginxpackname
    mv -f $nginxinitname /etc/init.d/nginx
    mv -f $nginxconfname $basedir/nginx/conf/nginx.conf
    chmod +x /etc/init.d/nginx
    sed -i  -e "s/@USER@/${user}/g" -e "s/@CPUCOUNT@/${cpucount}/g" $basedir/nginx/conf/nginx.conf
    cp /application/nginx/html/* /data/htdocs/
egrep -qx "/application/relys/nginx/GeoIP/lib" /etc/ld.so.conf
if [ $? -ne 0 ]; then
cat >>/etc/ld.so.conf<<EOF
/application/relys/nginx/GeoIP/lib
/application/relys/nginx/pcre/lib
EOF
fi
    ldconfig
    ln -s ${basedir}/nginx /usr/local/
    egrep -qx "/etc/init.d/nginx start" /etc/rc.local || echo  "/etc/init.d/nginx start" >> /etc/rc.local
    /etc/init.d/nginx start
}

function nginx_bulid() {
    mkdir -p $basedir /data/logs /data/htdocs
    chmod 777 /data/logs
    rpm -qa |grep wget &>/dev/null|| yum install wget -y &>/dev/null
    wget -q $packdownurl$nginxpackname  'http://d1aegnnxokxfi0.cloudfront.net/package/nginx_conf.tar.gz'
    wget -q -P /etc/init.d/ $initurl$nginxinitname
    tar xf $nginxpackname
    nginx_dir=`echo ${nginxpackname} |sed 's/.tar.gz//'`
    cd ${nginx_dir}
    ./configure --user=ec2-user --group=ec2-user --prefix=$basedir/nginx --with-http_stub_status_module --with-http_ssl_module --with-http_gzip_static_module --with-ipv6 --with-http_geoip_module --with-pcre --with-jemalloc
    make && make install
    cd ..
    tar xf 'nginx_conf.tar.gz' -C $basedir/nginx/conf/
    chmod +x /etc/init.d/nginx
    mkdir  /application/nginx/status
    mv -f $basedir/nginx/conf/nginx.conf.tpl $basedir/nginx/conf/nginx.conf
    sed -i  -e "s/@USER@/${user}/g" -e "s/@CPUCOUNT@/${cpucount}/g" $basedir/nginx/conf/nginx.conf
    cp ${basedir}/nginx/html/* /data/htdocs/
    ln -s ${basedir}/nginx /usr/local/
    ln -s ${basedir}/nginx/sbin/nginx /usr/local/bin
    egrep -qx "/etc/init.d/nginx start" /etc/rc.local || echo  "/etc/init.d/nginx start" >> /etc/rc.local
    /etc/init.d/nginx start
}

function mysql_install() {
    id mysql || useradd  mysql
    mkdir -p /data/logs /data/htdocs /data/mysqldata /data/mysqllogs/slow /data/mysqllogs/bin-log
    chown -R $user:$user /data/htdocs
    chown mysql:mysql /data/mysqldata
    chown -R mysql:mysql /data/mysqllogs /data/mysqldata
    chmod 777 /data/logs
    rpm -qa |grep wget &>/dev/null|| yum install wget -y &>/dev/null
    wget $packdownurl$mysqlpackname $initurl$mysqlinitname $initurl$mysqlconfname >/dev/null
    ls /usr/local/mysql &>/dev/null &&  mv /usr/local/mysql /usr/local/mysql.bak
    tar xf $mysqlpackname -C /usr/local/
    mv /usr/local/mysql-5.6.17-linux-glibc2.5-x86_64 /usr/local/mysql
    mv -f $mysqlconfname /etc/my.cnf
    mv -f $mysqlinitname /etc/init.d/mysqld
    chmod +x /etc/init.d/mysqld
    sed -i  -e "/bind-address/s/@IPIN@/127.0.0.1/g" -e "/thread_concurrency/s/@CPUCOUNT@/$cpucount/g" -e "/innodb_buffer_pool_size/s/@RAM2@/$RAM2/g" -e "/innodb_thread_concurrency/s/@CPUCOUNT@/$cpucount/g" /etc/my.cnf
    /usr/local/mysql/scripts/mysql_install_db --basedir=/usr/local/mysql --datadir=/data/mysqldata --defaults-file=/etc/my.cnf --user=mysql
    MYSQLBIN_PATH="/usr/local/mysql/bin"
    egrep -q '(^PATH=|^export PATH=)' /etc/profile  || echo "PATH=$MYSQLBIN_PATH:\$PATH:"  >> /etc/profile
    if [ $? -ne 0 ]; then
        sed  -r -i -e  '/(^PATH=|^PATH=)/s/:$//;' -e  "/(^PATH=|^PATH=)/s;$;:$MYSQLBIN_PATH:;"  /etc/profile
    fi
    source /etc/profile
    ln -s /usr/local/mysql/bin/mysql /usr/local/bin
    egrep -qx "/etc/init.d/mysqld start" /etc/rc.local || echo  "/etc/init.d/mysqld start" >> /etc/rc.local
    /etc/init.d/mysqld  start
}

function php_install() {
    mkdir -p /application/ /data/logs  /data/htdocs
    chmod 777 /data/logs
    if [[ ${phppackname} -eq 6 ]]; then
        php_bulid
        return
    fi
    wget $packdownurl$phppackname  $initurl$phpinitname >/dev/null
    tar xf $phppackname -C $basedir && rm  -f $phppackname
    wget -q -P $basedir/php/etc/ $initurl$phpconfname
    sed -i "s/@USER@/$user/g" $basedir/php/etc/$phpconfname
    mv -f $basedir/php/etc/$phpconfname $basedir/php/etc/php-fpm.conf
    mv -f $phpinitname /etc/init.d/php-fpm
    chmod +x /etc/init.d/php-fpm

egrep -qx "/application/relys/php/mhash/lib" /etc/ld.so.conf
if [ ! $? -eq 0 ]; then
cat >>/etc/ld.so.conf<<EOF
/application/relys/php/libiconv/lib
/application/relys/php/libltdl/lib
/application/relys/php/libmcrypt/lib
/application/relys/php/mhash/lib
EOF
fi
    ldconfig
    egrep -qx "/etc/init.d/php-fpm start" /etc/rc.local || echo  "/etc/init.d/php-fpm start" >> /etc/rc.local
    ln -s $basedir/php/bin/php /usr/local/bin/
    ln -s $basedir/php/bin/php-config /usr/local/bin/
    ln -s $basedir/php/bin/phpize /usr/local/bin/
    ln -s $basedir/php/bin/composer /usr/local/bin/
    ln -s $basedir/php /usr/local/
    /etc/init.d/php-fpm start
}

function php_bulid() {
    DownUrl='http://package.brotlab.net:8086/package/bulid_php'
    ConfUrl='http://package.brotlab.net:8086/package/init'
    PHP_Pack='php-5.6.16.tar.gz'
    InstallPath='/application/php'

    [[ -e '/usr/local/lib64' ]] && grep -q '/usr/local/lib64' /etc/ld.so.conf || echo '/usr/local/lib64' >> /etc/ld.so.conf
    grep -q '/usr/local/lib' /etc/ld.so.conf || echo '/usr/local/lib' >> /etc/ld.so.conf
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
    './configure'  "--prefix=${InstallPath}" "--with-config-file-path=${InstallPath}/etc" '--enable-fpm' '--with-fpm-user=ec2-user' '--with-fpm-group=ec2-user' '--with-mysql=mysqlnd' '--with-mysqli=mysqlnd' '--with-pdo-mysql=mysqlnd' '--with-iconv-dir' '--with-freetype-dir' '--with-jpeg-dir' '--with-png-dir' '--with-zlib' '--with-libxml-dir' '--enable-xml' '--disable-rpath' '--enable-bcmath' '--enable-shmop' '--enable-sysvsem' '--enable-inline-optimization' '--with-curl' '--enable-mbregex' '--enable-mbstring' '--with-mcrypt' '--enable-ftp' '--with-gd' '--enable-gd-native-ttf' '--with-openssl' '--with-mhash' '--enable-pcntl' '--enable-sockets' '--with-xmlrpc' '--enable-zip' '--enable-soap' '--with-gettext' '--enable-sysvshm' '--with-pdo-pgsql' '--enable-sysvmsg' '--with-bz2' '--with-pgsql' '--with-gmp'

    make -j${cpu_num}
    make install
    cd ${curr_path}
    rm -fr ${php_name}

    #下载php-fpm.conf及php.ini
    wget -q -P ${InstallPath}/etc/ ${ConfUrl}/php-fpm.conf.tpl ${ConfUrl}/php5.6.ini.tpl
    #修改php-fpm运行用户
    sed -i "s/@USER@/${user}/g" ${InstallPath}/etc/php-fpm.conf.tpl
    php_child_num=$((${RAM2}*2/15))
    sed -i "s/@CHILD@/$php_child_num/g" ${InstallPath}/etc/php-fpm.conf.tpl
    #修改php扩展路径
    sed -i "/^extension_dir/cextension_dir='${InstallPath}/lib/php/extensions/no-debug-non-zts-20131226/'" ${InstallPath}/etc/php5.6.ini.tpl
    #改名
    mv ${InstallPath}/etc/php-fpm.conf.tpl ${InstallPath}/etc/php-fpm.conf
    mv ${InstallPath}/etc/php5.6.ini.tpl ${InstallPath}/etc/php.ini
    #使用pecl安装memcached，igbinary,redis扩展
    ${InstallPath}/bin/pecl install igbinary
    echo | ${InstallPath}/bin/pecl install memcached
    echo | ${InstallPath}/bin/pecl install memcache
    #安装composer
    ${InstallPath}/bin/php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
    ${InstallPath}/bin/php 'composer-setup.php' --install-dir=${InstallPath}/bin/ --filename=composer
    ${InstallPath}/bin/php -r "unlink('composer-setup.php');" 2&1 > /dev/null

    ln -s ${InstallPath}/bin/composer /usr/local/bin/
    ln -s ${InstallPath} /usr/local/
    ln -s ${InstallPath}/bin/php /usr/local/bin/
    ln -s ${InstallPath}/bin/phpize /usr/local/bin/
    ln -s ${InstallPath}/bin/php-config /usr/local/bin/
    ln -s ${InstallPath}/bin/pecl /usr/local/bin/
    ln -s ${InstallPath}/bin/composer /usr/local/bin/

    #判断当前路径及/etc/init.d/有没有php-fpm5.6的文件，下载php启动文件到/etc/init.d/
    wget -q -P /etc/init.d/ ${ConfUrl}/php-fpm
    chmod +x /etc/init.d/php-fpm
    mkdir -p /data/logs/
    chmod 777 /data/logs

    /etc/init.d/php-fpm start
    chkconfig php-fpm on
}

function zabbix_agent_install() {
    if `grep "CentOS release 5.* (Final)" /etc/issue >/dev/null`;then
        rpm -qa | grep zabbix-2.2.5-1 || rpm -Uvh http://d1aegnnxokxfi0.cloudfront.net/zabbix/el5/zabbix-2.2.5-1.el5.x86_64.rpm
        rpm -qa | grep zabbix-agent-2.2.5-1 || rpm -Uvh http://d1aegnnxokxfi0.cloudfront.net/zabbix/el5/zabbix-agent-2.2.5-1.el5.x86_64.rpm
    else
        rpm -qa | grep zabbix-2.2.5-1 || rpm -Uvh http://d1aegnnxokxfi0.cloudfront.net/zabbix/el6/zabbix-2.2.5-1.el6.x86_64.rpm
        rpm -qa | grep zabbix-agent-2.2.5-1 || rpm -Uvh http://d1aegnnxokxfi0.cloudfront.net/zabbix/el6/zabbix-agent-2.2.5-1.el6.x86_64.rpm
    fi
        sed -i -e "/^Server=/cServer=s.zabbix.brotlab.net,p1.zabbix.brotlab.net" -e "/^ServerActive=/cServerActive=s.zabbix.brotlab.net,p1.zabbix.brotlab.net" -e "/^Hostname=/cHostname=`hostname`" /etc/zabbix/zabbix_agentd.conf
        mkdir -p /etc/zabbix/scripts/
        rm -f /etc/zabbix/zabbix_agentd.d/userparameter_mysql.conf
        rpm -qa |grep wget &>/dev/null || yum install wget -y
        ls /etc/zabbix/scripts/monitor_mysql &>/dev/null && mv /etc/zabbix/scripts/monitor_mysql  /tmp/monitor_mysql.bak
        wget -q -P /etc/zabbix/scripts/ http://d1aegnnxokxfi0.cloudfront.net/zabbix/config/monitor_mysql
        chmod +x /etc/zabbix/scripts/monitor_mysql
        ls  /etc/zabbix/zabbix_agentd.d/mysql.status.conf &>/dev/null && mv /etc/zabbix/zabbix_agentd.d/mysql.status.conf /tmp/mysql.status.conf
        wget -q -P /etc/zabbix/zabbix_agentd.d/ http://d1aegnnxokxfi0.cloudfront.net/zabbix/config/mysql_status.conf
        /etc/init.d/zabbix-agent start
        chkconfig zabbix-agent on
}

echo "1)完全安装"
echo "2)仅初始化系统环境(优化系统参数)"
echo "3)仅yum安装依赖库"
echo "4)安装nginx"
echo "5)安装mysql"
echo "6)安装php"
echo "7)安装zabbix客户端"
echo "8)安装Java环境"
echo "9)安装iptables"

read -p "输入数字选择安装过程(q键退出): " SET

case $SET in
    1)
        php_ver_choose
        basic_parse_optimize
        init_yum_install
        nginx_bulid
        mysql_install
        php_install

        if [[ $if_lan == [yY] ]] || [[ $if_lan == yes ]] || [[ $if_lan == YES ]]; then
            exit 0
        else
            zabbix_agent_install
            iptables_install
        fi
    ;;

    2)
    basic_parse_optimize
    ;;

    3)
    init_yum_install
    ;;

    4)
    init_yum_install
    nginx_bulid
    ;;

    5)
    init_yum_install
    mysql_install
    ;;

    6)
    php_ver_choose
    init_yum_install
    php_install
    ;;

    7)
    zabbix_agent_install
    ;;

    8)
    java_install
    ;;

    9)
    iptables_install
    ;;

    q)
    exit
    ;;

    *)
    请输入正确序号
    sh $0
    ;;
esac
