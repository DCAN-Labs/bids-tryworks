source /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2/venv/bin/activate
python /group_shares/fnl/bulk/code/internal/GUIs/bidsgui2/manage.py runserver 8003 &
chromium-browser http://127.0.0.1:8003/dicoms/
