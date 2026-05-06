# main.py
import asyncio
import os
from datetime import datetime

from core.pipeline import full_content_pipeline
from connectors.outputs.telegram_logger import TelegramLogger

async def run_daily_engine():
    start_time = datetime.utcnow()
    
    logger = TelegramLogger()
    await logger.log_event("INFO", "🚀 Iniciando Stellar Content Engine - Modo Automático", 
                          {"time": start_time.isoformat()})

    try:
        items = full_content_pipeline()
        
        await logger.log_event("SUCCESS", 
                              f"✅ Engine completado correctamente | {len(items)} items procesados", 
                              {"duration_seconds": (datetime.utcnow() - start_time).seconds,
                               "top_score": max((i.score for i in items), default=0)})

    except Exception as e:
        await logger.log_event("ERROR", f"❌ Engine falló: {str(e)}", {"error": str(e)})
        raise


if __name__ == "__main__":
    asyncio.run(run_daily_engine())