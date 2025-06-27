from uvicorn.workers import UvicornWorker
import asyncio
from typing import Optional

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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cleanup_task: Optional[asyncio.Task] = None

    async def _serve(self) -> None:
        self._cleanup_task = None
        try:
            await super()._serve()
        finally:
            if self._cleanup_task:
                try:
                    await self._cleanup_task
                except Exception as e:
                    self.log.warning(f"Error during final cleanup: {str(e)}")

    def handle_exit(self, sig: int, frame) -> None:
        """Handle process termination gracefully"""
        self.log.info("Received signal %s. Starting graceful shutdown", sig)
        
        # Create cleanup task if not already running
        if not self._cleanup_task:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(self._cleanup())
            
        super().handle_exit(sig, frame)

    async def _cleanup(self) -> None:
        """Cleanup connections and resources"""
        try:
            # Get the app instance
            app = self.app.load()
            
            # If the app has a cleanup method, call it
            if hasattr(app, 'cleanup') and callable(app.cleanup):
                await app.cleanup()
                
            # Small delay to allow connections to close gracefully
            await asyncio.sleep(0.1)
        except Exception as e:
            self.log.warning(f"Error during connection cleanup: {str(e)}")
