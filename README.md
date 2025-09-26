# py-ai

Python ai application

# Create txt file

pip freeze > requirements.txt

# run

uvicorn src.app:app --reload

# install development dependencies and update requirements.txt

pip freeze > requirements.txt

pip3 install virtualenv
python3 -m venv applicationvenv
. applicationvenv/bin/activate

# setup database

install postgresql
run sudo apt-get -y install postgresql-16-pgvector

# Build local

docker build -t tiktokapi:latest .

docker run -p 8000:8000 \
 -v $(pwd)/src:/app/src \
 -e GOOGLE_API_KEY="AIzaSyBITntpOVk-CckA2vXDPCLp0WavU355_9g" \
 -e POSTGRES_HOST="103.175.147.108" \
 -e POSTGRES_USER="postgres" \
 -e POSTGRES_PASSWORD="postgres_123" \
 -e POSTGRES_PORT="5432" \
 -e SECRET_KEY="Yh2k7QSu4l8CZg5p6X3Pna9L0Miy4D3Bvt0JVr87UcOj69Kqw5R2Nmf4FWs03Hdx" \
 -e ALGORITHM="HS256" \
 -e ISSUER="https://account.biz5s.com" \
 -e AUDIENCE="Tai Nguyen" \
 -e MONGO_URL="mongodb://admin:G5HY75FFI9@103.175.147.108:27017" \
 -e MONGO_DB="Biz5sDb-Dev" \
 -e PG_URL="postgresql+psycopg2://postgres:postgres_123@103.175.147.108:5432/rag-dev" \
 --rm tiktokapi:latest

# note: has issue with mcp_use. can remove from requirements.txt and install manually

# day la build manualy. su dung cac buoc sau cho x86_64

docker tag tiktokapi:latest tainguyen1501/py-social:latest
docker push tainguyen1501/py-social:latest

# Buid x86_64 cho cluster . NOTE check bellow is doc. just run docker pull mcr.microsoft.com/playwright:focal

docker pull mcr.microsoft.com/playwright:focal
docker build . -t tiktokapi:latest
docker run -v TikTokApi --rm tiktokapi:latest python3 your_script.py

# 1. Bước 1 — Bật Docker Buildx

docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap

# Bước 2 — Build image cho x86_64

docker buildx build --platform linux/amd64 -t tainguyen1501/py-social:latest --push .

# Bước 3 — Kiểm tra image

docker buildx imagetools inspect tainguyen1501/py-social:latest
