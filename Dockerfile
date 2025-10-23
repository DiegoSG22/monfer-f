
# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos al contenedor
COPY requirements.txt .

# Instalar dependencias del sistema (psycopg2 puede necesitar esto)
# Comentado temporalmente para probar si causa el error de construcción
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación al contenedor
COPY . .

# Exponer el puerto 8080 (Fly.io suele esperar este puerto)
EXPOSE 8080

# Variable de entorno para el puerto (buena práctica)
ENV PORT=8080

# Ejecutar gunicorn cuando el contenedor se inicie
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]