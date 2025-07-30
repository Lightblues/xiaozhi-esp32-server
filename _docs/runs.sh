git clone https://github.com/xinnan-tech/xiaozhi-esp32-server
gsw -c eason
git remote rename origin upstream
# ... fork
git remote add gh https://github.com/Lightblues/xiaozhi-esp32-server

cd main/xiaozhi-server

uv venv -p 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

mkdir data
cp config.yaml data/.config.yaml

# https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/2
export DYLD_LIBRARY_PATH=/usr/local/lib:/opt/homebrew/lib:$DYLD_LIBRARY_PATH
python app.py
