import os
import uvicorn

if __name__ == "__main__":
    # Получаем порт из переменной окружения или используем 8000 по умолчанию
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting server on port {port}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False  # Отключаем reload в production
    )