
        # !/bin/bash -
    
        yum
        install
        awslogs - y
    
        cat >> / etc / awslogs / awscli.conf << EOF
        [plugins]
        cwlogs = cwlogs
        [default]
        region = ap-northeast-1
        EOF
    
        cat > / etc / awslogs / awslogs.conf << EOF
        [general]
        state_file = / var / lib / awslogs / agent - state
        EOF
        
                [oas-uqp]
                datetime_format = [%Y-%m-%d %H:%M:%S]
                time_zone = UTC
                file = /data/a.log
                buffer_duration = 5000
                log_stream_name = oas-uqp-web1
                initial_position = end_of_file
                multi_line_start_pattern = {datetime_format}
                log_group_name = oas-uqp
            
                [oas-uqp]
                datetime_format = [%Y-%m-%d %H:%M:%S]
                time_zone = UTC
                file = /data/a.log
                buffer_duration = 5000
                log_stream_name = oas-uqp-web1
                initial_position = end_of_file
                multi_line_start_pattern = {datetime_format}
                log_group_name = oas-uqp
            