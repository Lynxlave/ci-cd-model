# ML Service - Blue-Green Deployment

## Описание

ML-сервис с REST API эндпоинтами:
- `/health` - возвращает статус и версию модели
- `/predict` - выполняет инференс

## Структура проекта

- `main.py` - FastAPI приложение
- `requirements.txt` - Python зависимости
- `Dockerfile` - конфигурация Docker образа
- `docker-compose.blue.yml` - Blue окружение (v1.0.0) с Nginx
- `docker-compose.green.yml` - Green окружение (v1.1.0) с Nginx
- `docker-compose.balancer.yml` - оба окружения с балансировкой трафика
- `nginx.conf` - конфигурация Nginx балансировщика
- `.github/workflows/deploy.yml` - GitHub Actions workflow

## Установка и запуск

### Локальный запуск

1. Соберите Docker образ:
```bash
docker build -t ml-service:v1 .
```

2. Запустите Blue окружение:
```bash
docker-compose -f docker-compose.blue.yml up -d
```

3. Проверьте работу:
```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"x": [1, 2, 3]}'
```

4. Для запуска Green окружения:
```bash
docker-compose -f docker-compose.green.yml up -d
```

## Blue-Green Deployment с Nginx

### Запуск с балансировкой трафика

Для запуска обоих окружений с балансировкой трафика между Blue и Green:

```bash
docker-compose -f docker-compose.balancer.yml up -d
```

Это запустит:
- Blue сервис на порту 8081 (v1.0.0)
- Green сервис на порту 8082 (v1.1.0)
- Nginx балансировщик на порту 8080, распределяющий трафик 50/50

### Проверка работы /health для обеих версий

**Проверка Blue напрямую:**
```bash
curl http://localhost:8081/health
# Ответ: {"status":"ok","version":"v1.0.0"}
```

**Проверка Green напрямую:**
```bash
curl http://localhost:8082/health
# Ответ: {"status":"ok","version":"v1.1.0"}
```

**Проверка через балансировщик (распределение трафика):**
```bash
# Несколько запросов покажут распределение между версиями
for i in {1..5}; do curl -s http://localhost:8080/health; echo ""; done
```

### Переключение трафика и откат

**Переключение всего трафика на Green:**
1. Отредактируйте `nginx.conf`:
```nginx
upstream ml_backend {
    server ml-service-green:8080;
}
```

2. Перезапустите Nginx:
```bash
docker-compose -f docker-compose.balancer.yml restart nginx
```

**Откат на Blue (при ошибках Green):**
1. Отредактируйте `nginx.conf`:
```nginx
upstream ml_backend {
    server ml-service-blue:8080;
}
```

2. Перезапустите Nginx:
```bash
docker-compose -f docker-compose.balancer.yml restart nginx
```

**Настройка весов для постепенного перехода (Canary):**
В `nginx.conf` можно настроить распределение трафика:
```nginx
upstream ml_backend {
    server ml-service-blue:8080 weight=9;    # 90% трафика
    server ml-service-green:8080 weight=1;  # 10% трафика
}
```

### Проверка работы

Проверьте через балансировщик (порт 8080):
```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"x": [0.4, -0.2, 0.1]}'
```

## CI/CD

GitHub Actions workflow автоматически собирает и пушит Docker образ при push в ветку `main`.

### Настройка секретов

В GitHub Secrets (Settings → Secrets and variables → Actions) добавьте:
- `CLOUD_TOKEN` - токен для деплоя через API
- `MODEL_VERSION` (опционально) - версия модели, по умолчанию v1.0.0

Примечание: `GITHUB_TOKEN` предоставляется автоматически GitHub Actions.

## Проверка результата

После деплоя проверьте:

**Health check:**
```bash
curl http://localhost:8080/health
```

Ожидаемый ответ:
```json
{
  "status": "ok",
  "version": "v1.0.0"
}
```

**Prediction:**
```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"x": [0.4, -0.2, 0.1]}'
```

Ожидаемый ответ:
```json
{
  "prediction": 1.0,
  "confidence": 0.603,
  "version": "v1.0.0"
}
```
