python3 scripts/filler.py & uvicorn src.main:app --host 0.0.0.0 --port $PORT
while ($true) {
    curl https://atp-rankings-data-visualization.onrender.com
    sleep 300
}