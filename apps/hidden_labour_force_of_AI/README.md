# Build and run

```bash
export BASE_URL_PATH=/hidden_labour_force_of_AI
export EXTERNAL_PORT=5101

docker-compose up --build
```

# NGINX proxy configuration

```nginx
location ~ ^/hidden_labour_force_of_AI(/.*)$ {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://localhost:8501;
}
```