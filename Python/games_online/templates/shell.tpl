#!/bin/bash -

yum install awslogs -y

cat >> /etc/awslogs/awscli.conf <<EOF
[plugins]
cwlogs = cwlogs
[default]
region = {{ region }}
EOF

cat > /etc/awslogs/awslogs.conf <<EOF
[general]
state_file = /var/lib/awslogs/agent-state
EOF

[{{ name }}]
{%- if dateFormat -%}
datetime_format = {{ dateFormat }}
{%- endif -%}
time_zone = UTC
file = {{ filePath }}
buffer_duration = 5000
log_stream_name = {{ logStream }}
initial_position = end_of_file
{%- if line_format -%}
multi_line_start_pattern = {{ lineFormat }}
{% endif %}
log_group_name = {{ logGroup }}
