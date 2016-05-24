#!/bin/bash -
read -p 'Please enter the FTP user running : (www) ' ftprun
read -p 'Please input an ftp login user : ' ftpuser
read -p 'Input password : ' ftppass
read -p 'Input user default path : ' ftppath

if [ -z ${ftprun} ];then
    ftprun=www
fi

yum install  vsftpd  db4 db4-utils -y

cat > /etc/vsftpd/vsftpd.conf <<EOF
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
anon_world_readable_only=NO
anon_upload_enable=NO
anon_mkdir_write_enable=NO
anon_other_write_enable=NO
guest_enable=YES
guest_username=@USER@
virtual_use_local_privs=YES
chroot_local_user=YES
user_config_dir=/etc/vsftpd/vconf
local_root=/data/htdocs
chown_uploads=YES
chown_username=@USER@
dirmessage_enable=YES
ftpd_banner=Welcome to OASGAMES FTP service.
listen=YES
#listen_address=127.0.0.1
listen_port=21
port_enable=YES
connect_from_port_20=YES
pasv_enable=YES
pasv_min_port=30000
pasv_max_port=30999
pasv_promiscuous=YES
idle_session_timeout=600
data_connection_timeout=1200
pam_service_name=vsftpd
userlist_enable=YES
userlist_file=/etc/vsftpd/
tcp_wrappers=YES
EOF

sed -i "s/@USER@/$ftprun/g" /etc/vsftpd/vsftpd.conf
if [ ! -z $ftpuser ] && [ ! -z $ftppass ];then
    echo $ftpuser >>  /etc/vsftpd/virtusers
    echo $ftppass >> /etc/vsftpd/virtusers
    db_load -T -t hash -f /etc/vsftpd/virtusers /etc/vsftpd/virtusers.db
    mkdir /etc/vsftpd/vconf/
    cat > /etc/vsftpd/vconf/$ftpuser <<EOF
    local_root=@path@
    write_enable=YES
    anon_world_readable_only=NO
    anon_upload_enable=YES
    anon_mkdir_write_enable=YES
    anon_other_write_enable=YES
EOF
    sed -i "s/@path@/$ftppath/" /etc/vsftpd/vconf/$ftpuser
else
    echo 'Username or password error ! '
fi

cat > /etc/pam.d/vsftpd <<EOF
#%PAM-1.0
auth      sufficient       /lib64/security/pam_userdb.so     db=/etc/vsftpd/virtusers
account sufficient      /lib64/security/pam_userdb.so     db=/etc/vsftpd/virtusers
EOF

/etc/init.d/vsftpd start
