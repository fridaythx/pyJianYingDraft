tar zcvf deploy.zip --exclude="*.pyc" http_server.py pyJianYingDraft requirements.txt startup.sh 
scp deploy.zip pi:/home/pi
# ssh pi 'source ~/.profile && tar zxvf deploy.zip -C pyJianYingDraft && cd pyJianYingDraft && pip install -r requirements.txt && ./startup.sh'
ssh pi 'tar zxvf deploy.zip -C pyJianYingDraft && cd pyJianYingDraft'
