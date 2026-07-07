import sys
from loguru import logger

# 1. Удаляем дефолтную настройку loguru (чтобы сообщения не дублировались)
logger.remove()

# 2. Настройка вывода в консоль (красиво, с цветами, уровень INFO и выше)
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    enqueue=True # Делает логирование асинхронным (безопасно для FastAPI и ботов)
)

# 3. Настройка записи в файл (строго, без лишних цветов, уровень DEBUG и выше)
logger.add(
    "logs/bot.log", 
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",     # Файл заполнился до 10 МБ? Создается новый, старый архивируется.
    retention="10 days",   # Хранить логи только за последние 10 дней (чтобы диск не переполнился).
    compression="zip",     # Старые логи сжимаются в zip для экономии места.
    enqueue=True           # Потокобезопасность
)

# 4. Перехватываем стандартный logging, чтобы все библиотеки писали в loguru
# В aiogram и apscheduler этого достаточно для перенаправления их логов
logger.patch(lambda record: record.update(name=record["name"].split(".")[0] if isinstance(record.get("name"), str) else record.get("name")))
