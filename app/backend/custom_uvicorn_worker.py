from uvicorn.workers import UvicornWorker
import asyncio
from typing import Optional
import signal

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
        "timeout_keep_alive": 30,  # Reduce keep-alive timeout
        "timeout_graceful_shutdown": 10,  # Add graceful shutdown timeout
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shutdown_complete = asyncio.Event()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._original_handler = None
        self._is_shutting_down = False

    async def _serve(self) -> None:
        self._cleanup_task = None
        try:
            # Set up signal handlers
            self._original_handler = signal.getsignal(signal.SIGTERM)
            signal.signal(signal.SIGTERM, lambda sig, frame: self._handle_signal(sig, frame))
            
            await super()._serve()
        finally:
            # Wait for cleanup to complete
            try:
                if self._cleanup_task:
                    await asyncio.wait_for(self._cleanup_task, timeout=20.0)  # Increased timeout
            except asyncio.TimeoutError:
                self.log.warning("Cleanup task timed out")
            except Exception as e:
                self.log.warning(f"Error during cleanup: {str(e)}")
            finally:
                # Restore original signal handler
                if self._original_handler:
                    signal.signal(signal.SIGTERM, self._original_handler)

    def _handle_signal(self, sig: int, frame) -> None:
        """Handle termination signal"""
        if self._is_shutting_down:
            self.log.warning("Already shutting down, ignoring signal")
            return
            
        self._is_shutting_down = True
        self.log.info(f"Received signal {sig}. Starting graceful shutdown")
        
        if not self._cleanup_task:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(self._cleanup())
        
        # Call parent's signal handler
        super().handle_exit(sig, frame)

    async def _cleanup(self) -> None:
        """Cleanup connections and resources"""
        try:
            # Get the app instance
            app = self.app.load()
            
            # Set shutdown event
            self._shutdown_complete.set()
            
            # If the app has a cleanup method, call it
            if hasattr(app, 'cleanup') and callable(app.cleanup):
                try:
                    await asyncio.wait_for(app.cleanup(), timeout=10.0)
                except asyncio.TimeoutError:
                    self.log.warning("App cleanup timed out")
                except Exception as e:
                    self.log.warning(f"Error during app cleanup: {str(e)}")
            
            # Close any remaining connections
            for task in asyncio.all_tasks():
                if task is not asyncio.current_task():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=5.0)
                    except (asyncio.TimeoutError, asyncio.CancelledError):
                        pass
                    except Exception as e:
                        self.log.warning(f"Error cancelling task: {str(e)}")
            
            # Small delay to allow connections to close gracefully
            await asyncio.sleep(0.5)
        except Exception as e:
            self.log.warning(f"Error during connection cleanup: {str(e)}")
        finally:
            # Ensure we always clear the shutdown event and flag
            self._shutdown_complete.clear()
            self._is_shutting_down = False
