FROM python:3.12

# تثبيت الأدوات اللازمة لبناء الحزم
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-distutils \
    gcc \
    cmake \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && apt-get clean

# إعداد مجلد العمل
WORKDIR /app

# نسخ ملفات المشروع
COPY . .

# ترقية pip وتثبيت المتطلبات
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# تشغيل التطبيق
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
