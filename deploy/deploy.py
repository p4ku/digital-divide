import os
import glob
import toml
import shutil
import subprocess


def load_config(config_path):
    """
    Load a TOML config file
    Example:
        [application]
        name = "hidden-labour-force-of-AI-app"
    """
    try:
        with open(config_path, 'r') as file:
            return toml.load(file)
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return None


def set_env_and_run_docker(config, dir_path, external_port):
    application_config = config.get('application', {})
    application_name = application_config.get('name', '')
    os.environ["APP_PATH"] = dir_path
    os.environ["BASE_URL_PATH"] = application_name
    os.environ["CONTAINER_NAME"] = f'strealmit-{application_name}'
    os.environ["EXTERNAL_PORT"] = str(external_port)

    docker_compose_path = os.path.join(dir_path, 'docker-compose.yml')
    print(f"Dir path: {dir_path}")
    print(f"Base URL Path: {application_name}")
    print(f"Container Name: {os.environ['CONTAINER_NAME']}")
    print(f"External Port: {os.environ['EXTERNAL_PORT']}")
    print(f"Docker Compose Path: {docker_compose_path}")

    print(f"Running docker-compose up -d for {dir_path}")
    subprocess.run(["docker-compose", "-f", docker_compose_path, "up", "--build", "-d"], cwd=dir_path)


def prepare_nginx_config(application_config, external_port):
    application_name = application_config.get('name', '')
    nginx_config = f"""
    location ~ ^/{application_name}(/.*)$ {{
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_pass http://localhost:{external_port};
    }}
    """
    return nginx_config


def reload_applications(apps_directory):
    external_port = 8501
    nginx_configs = []
    for dir_path in glob.glob(os.path.join(apps_directory, '*/')):
        print(f"Checking {dir_path}")
        config_path = os.path.join(dir_path, 'config.toml')
        if os.path.isfile(config_path):
            config = load_config(config_path)
            if config:
                application_config = config.get('application', {})
                nginx_config = prepare_nginx_config(application_config, external_port)
                nginx_configs.append(nginx_config)
                set_env_and_run_docker(config, dir_path, external_port)
        else:
            print(f"No config file found in {dir_path}")

        external_port += 1

    full_nginx_config = "\n".join(nginx_configs)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    nginx_config_path = os.path.join(script_dir, 'nginx_config', 'nginx.config')

    with open(nginx_config_path, 'w') as nginx_file:
        nginx_file.write(full_nginx_config)

    # Copy the Nginx configuration to /etc/nginx/snippets/
    nginx_snippets_path = '/etc/nginx/snippets/ddivs.config'
    shutil.copy(nginx_config_path, nginx_snippets_path)
    print(f"Nginx Configuration copied to {nginx_snippets_path}")

    # Restart Nginx
    subprocess.run(["sudo", "systemctl", "restart", "nginx"])
    print("Nginx has been restarted.")


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__))

    apps_directory = os.path.abspath(os.path.join(script_dir, '../apps'))
    reload_applications(apps_directory)
