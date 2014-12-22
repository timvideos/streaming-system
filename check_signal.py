import requests
import shutil
import config

loaded_config = config.config_load()
groups = loaded_config.groups()

for group in groups:
    encoder_url = loaded_config.config(group)['flumotion-encoder']
    url = "http://" + encoder_url + ":8081/loop.raw"
    print "scanning " + group
    try:
        r = requests.head(url, stream=True)
    except:
        print group + " is down..."
        continue
    if r.headers['content-type'] == 'None':
         print "NO SIGNAL in " + group
         try:
             shutil.copy('/home/ubuntu/no_signal.png','/srv/'+group+'/00000001.png')
         except Exception, e:
            raise shutil.Error('Unable to copy no_signal.png\n%s' % e)
