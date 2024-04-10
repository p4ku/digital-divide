# Build and run

```bash
export BASE_URL_PATH=/internet_users_by-country
export EXTERNAL_PORT=5102

docker-compose up --build
```

# NGINX proxy configuration

```nginx
location ~ ^/internet_users_by-country(/.*)$ {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass http://localhost:8502;
}
```