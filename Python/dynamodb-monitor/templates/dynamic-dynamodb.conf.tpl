[global]
aws-access-key-id: {{ aws_access_key }}
aws-secret-access-key-id: {{ aws_access_secret }}
region: {{ aws_region }}
check-interval: 60

[logging]
log-level: info
log-file: {{ log_file }}

[default_options]
increase-consumed-reads-unit: percent
increase-consumed-reads-scale: {70:30, 80:30, 90: 50}
increase-consumed-writes-unit: percent
increase-consumed-writes-scale: {70:30, 80:30, 90: 50}

#表读取相关配置
enable-reads-up-scaling = true
enable-reads-down-scaling = true
#reads-upper-threshold: 50
reads-lower-threshold: 60
#increase-reads-with: 50
decrease-reads-with: 20
increase-reads-unit: percent
decrease-reads-unit: percent
min-provisioned-reads: 5
max-provisioned-reads: 500
#表写入相关配置
enable-writes-up-scaling = true
enable-writes-down-scaling = true
#writes-upper-threshold: 50
writes-lower-threshold: 60
#increase-writes-with: 50
decrease-writes-with: 20
increase-writes-unit: percent
decrease-writes-unit: percent
min-provisioned-writes: 5
max-provisioned-writes: 500
allow-scaling-down-reads-on-0-percent: true
allow-scaling-down-writes-on-0-percent: true

[table: {{ table }}]
[gsi: .* table: {{ table }}]