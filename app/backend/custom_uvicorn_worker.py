from uvicorn.workers import UvicornWorker
import aiohttp
import asyncio

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "format": "%(asctime)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "root": {"handlers": ["default"]},
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
    },
}


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "log_config": logconfig_dict,
    }

    async def _serve(self) -> None:
        try:
            await super()._serve()
        finally:
            # Ensure all aiohttp connections are closed
            await self._cleanup_connections()

    async def _cleanup_connections(self) -> None:
        try:
            # Close any remaining aiohttp sessions
            await aiohttp.ClientSession.close_all()
        except Exception as e:
            self.log.warning(f"Error during connection cleanup: {str(e)}")
            
        # Wait a bit for connections to close
        await asyncio.sleep(1)
