# Build and run

```bash
EXTERNAL_PORT=8501 BASE_URL_PATH=app1 docker-compose up --build
```

or 

```bash
docker build -t streamlit .

docker run -p 8501:8501 streamlit
```

# NGINX proxy configuration

```nginx
location ~ ^/app1(/.*)$ {
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

# Embedding app IN HTML 

```html
<iframe
  src="//URL/app1/?embed=true&embed_options=disable_scrolling&embed_options=show_colored_line"
  height="800"
  style="width:100%;border:none;"
>
```