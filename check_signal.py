import requests
import shutil
import config

groups = config.config_load().groups()

for group in groups:
    url = "http://" + group + ".encoder.timvideos.us:8081/loop.raw"
    print "scanning " + group
    try:
        r = requests.get(url, stream=True)
    except:
        print group + " is down..."
        continue
    if r.headers['content-type'] == 'None':
         print "NO SIGNAL in " + group
         try:
             shutil.copy('/home/ubuntu/no_signal.png','/srv/'+group+'/00000001.png')
         except Exception, e:
            raise shutil.Error('Unable to copy no_signal.png\n%s' % e)
