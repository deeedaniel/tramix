# tramix

AI-powered web application that aims to streamline the process of creating playlists for DJs. By utilizing harmonic mixing theory and audio metadata, the platform will suggest tracks that are compatible with one another.

# backend

## create virtual environment (do this only once):

python -m venv .venv

- or use python3

## activate virtual environment:

source .venv/bin/activate

## install requirements

pip install -r requirements.txt

## setup environment variables

cp .env.example .env

- then add your GETSONGKEY_API_KEY to .env

## run the server

fastapi dev main.py

# frontend

## install dependencies

npm install

## run server

npm run dev
