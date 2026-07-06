import time
from functools import wraps
from loguru import logger

def log_function_call(func):
    """
    Декоратор для асинхронных функций, который логирует
    вход, выход, время выполнения и ошибки.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Формируем строку с аргументами
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        
        logger.debug(f"--> Entering {func.__name__}({signature})")
        
        start_time = time.time()
        try:
            # Выполняем саму функцию
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.debug(f"<-- Exiting {func.__name__} (took {execution_time:.4f}s)")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.exception(
                f"!!! Exception in {func.__name__} after {execution_time:.4f}s: {e}"
            )
            raise # Перевыбрасываем исключение
            
    return wrapper
