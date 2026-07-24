import logging

log = logging.getLogger(__name__)

async def error_handler(update, context):
    """Global error handler"""
    error = context.error
    
    # Log the error
    log.exception("Exception while handling an update:", exc_info=error)
    
    # You can add specific error handling here
    # For now, we just log and continue