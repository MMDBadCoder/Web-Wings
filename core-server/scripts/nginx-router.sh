#!/bin/bash

# Define input as pairs of domain:port
# Example: domains=("mmd-net.ir:7000" "web-wings.ir:8000")
# Command: ./generate_and_run_nginx.sh mmd-net.ir:7000 web-wings.ir:8000
domains=("$@")

# Define the output config file
nginx_conf="nginx.conf"

# Start generating nginx.conf
cat <<EOL > $nginx_conf
events {}

http {
EOL

# Loop through each domain:port pair to generate server blocks
for domain_port in "${domains[@]}"; do
    # Separate the domain and port
    domain="${domain_port%:*}"
    port="${domain_port#*:}"

    # Append server block to nginx.conf
    cat <<EOL >> $nginx_conf
    server {
        listen 80;
        server_name $domain;

        location / {
            proxy_pass http://host.docker.internal:$port/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }

EOL
done

# Close the http block
echo "}" >> $nginx_conf

# Run Nginx Docker container with the generated configuration
docker run -d --network host --name nginx-proxy -v $(pwd)/$nginx_conf:/etc/nginx/nginx.conf nginx:latest
