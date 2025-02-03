![quota-manafment](https://github.com/user-attachments/assets/0e7ac8b0-09d4-455a-8d6e-cdddafe2c4a9)


# PS: всё делалось, собиралось и выкладывалось при помощи ChatGPT 4o и o3-mini-high, сам я хз как это всё делать с нуля, но получилось то что хотел, делюсь со всеми, может пригодится
## админка по пути /admin

# Управление серверами

Это проект для учета выделнного пространства на серверах.

## Используемые технологии

- **Python**: Основной язык программирования
- **Flask**: Веб-фреймворк для создания интерфейсов
- **Gunicorn**: WSGI сервер для продакшн запуска
- **HTML/CSS**: Для фронтенда

## Зависимости

- Python 3.11+
- Flask
- Gunicorn
- pipx
- python3-venv

## Установка

### Шаг 1: Клонирование репозитория

Сначала клонируйте репозиторий проекта и перейдите в каталог проекта:

```bash
cd /opt
git clone https://github.com/Ttolyanich/quota-management.git
cd quota-management
```

### Шаг 2: Установка пакетов и настройка

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip gunicorn nginx -y
```
Создание и активация виртуального окружения:
```bash
python3 -m venv /opt/quota-managment/venv
source /opt/quota-managment/venv/bin/activate
pip install --break-system-packages flask gunicorn
```
Установка Flask и Gunicorn:
```bash
pip install flask gunicorn
```

### Шаг 3: Настройка автозапуска (systemd)

Чтобы приложение запускалось автоматически при загрузке системы, создайте файл службы:

1. Создайте файл службы:

```bash
sudo nano /etc/systemd/system/quota-managment.service
```

2. Вставьте в него следующее содержимое:

```ini
[Unit]
Description=Quota Managment
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/quota-managment
ExecStart=/opt/quota-managment/venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 app:app

[Install]
WantedBy=multi-user.target
```

3. Перезагрузите systemctl, активируйте службу и запустите её:

```bash
sudo systemctl daemon-reload
sudo systemctl enable quota-managment.service
sudo systemctl start quota-managment.service
```

Теперь ваше приложение будет автоматически запускаться при загрузке системы.

Настройка Nginx для проксирования:
```bash
sudo nano /etc/nginx/sites-enabled/quota-managment
```

```bash
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Перезапустить NGINX
```bash
systemctl restart nginx
```

## Зависимости

- Python3
- Flask
- Gunicorn
