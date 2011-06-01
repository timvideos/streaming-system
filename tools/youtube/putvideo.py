#!/usr/bin/python

"""Uploads videos in a directory to Youtube's SFTP server."""

import os
import logging.config
import pexpect
import re
import sys
import socket
import time
import tempfile

USERNAME = os.environ['YOUTUBE_USER']
HOST = "%s.xfer.youtube.com" % USERNAME.lower()
PRIVATE_KEY = os.path.expanduser("~/.ssh/youtube")
PASSWORD = os.environ['YOUTUBE_PASSWORD']

PROMPT = 'sftp> '
SURE = 'Are you sure you want to continue connecting (yes/no)?'
LS_REGEX = re.compile(r'^(?P<type>.)(?P<permissions_user>...)(?P<permissions_group>...)(?P<permissions_other>...)\s+(?P<number>[0-9]+)\s(?P<user>[^ ]+)\s+(?P<group>[^ ]+)\s+(?P<size>[^ ]+)\s+(?P<date>............) (?P<filename>.+)$')
PROGRESS_REGEX = re.compile(r'^(?P<filename>[^ ]*)\s+(?P<percentage>[0-9]+)%\s+(?P<uploaded>[0-9]+)(?P<uploaded_type>[^ ]+)\s+(?P<speed>[^ ]+)\s+(?P<eta>[^ ]+)(\s+)?(ETA)?$')

def getfiles(path):
  files = {}
  for filename in os.listdir(path):
    if not filename.endswith('.flv'):
      continue
    files[filename] = os.stat(os.path.join(path, filename)).st_size
  return files


def guess_event(date):
  # If Friday it's probably SLUG
  if date.tm_wday == 4:
    return {'name': 'Sydney Linux User Group',
            'shortname': 'SLUG',
            'tags': 'Linux, open source, free software, foss, oss',
            }

  # If it's a Thursday it could be SyPy or FP Syd
  if date.tm_wday == 3:
    # First Thursday is SyPy
    if date.tm_mday < 14:
      return {'name': 'Sydney Python User Group',
              'shortname': 'SyPy',
              'tags': 'Python, programming',
              }
    # Probably FP-Syd
    else:
      return {'name': 'Functional Programming Sydney',
              'shortname': 'FP-Syd',
              'tags': 'functional, programming',
              }

  return {'name': 'Unknown Tech Talk',
          'shortname': 'Unknown Tech Talk',
          'tags': '',
          }


def sftp_listdir(sftp, dirname):
  logging.info('Listing %s', dirname)
  sftp.sendline("ls -l %s" % dirname)
  sftp.expect(PROMPT)

  lines = sftp.before.split("\n")[1:]

  details = {}
  for line in lines:
    if not line:
      continue
    m = LS_REGEX.match(line)
    if not m:
      logging.warn('Regex did not match %r!', line)
      continue
    g = m.groupdict()
    details[g['filename'].strip()] = long(g['size'].strip())
  logging.info('Found following files %s', details)
  return details


def sftp_mkdir(sftp, dirname):
  logging.info('Making dir %s', dirname)
  sftp.sendline("mkdir %s" % dirname)
  sftp.expect(PROMPT)
  logging.info('Result: %s', sftp.before)


t = {'GB': 1e9,
     'MB': 1e6,
     'KB': 1e3}


def sftp_put(sftp, infilename, outfilename, progress):
  size = os.stat(infilename).st_size
  logging.info('Uploading %s (%sMB) to %s', infilename, size/1e6, outfilename)

  sftp.sendline("put %s %s" % (infilename, outfilename))

  while True:
    sftp.expect([PROMPT, '\r'])

    if sftp.after == '\r':
      m = PROGRESS_REGEX.match(sftp.before.strip())
      if not m:
        logging.warn('Progress regex did not match %r', sftp.before.strip())
        continue

      d = m.groupdict()
      progress(**d)

    elif sftp.after == PROMPT:
      logging.info('Uploaded!')
      return

def sftp_get(sftp, infilename, outfilename, progress):
  logging.info('Downloading %s to %s', infilename, outfilename)

  sftp.sendline("get %s %s" % (infilename, outfilename))

  while True:
    sftp.expect([PROMPT, '\r'])

    if sftp.after == '\r':
      m = PROGRESS_REGEX.match(sftp.before.strip())
      if not m:
        logging.warn('Progress regex did not match %r', sftp.before.strip())
        continue

      d = m.groupdict()
      progress(**d)

    elif sftp.after == PROMPT:
      logging.info('Downloaded!')
      return


def sftp_write(sftp, filename, data):
  logging.info('Writing to %s', filename)
  logging.debug(data)
  f = tempfile.NamedTemporaryFile('w+', delete=False)
  f.write(data)
  f.close()
  sftp_put(sftp, f.name, filename, lambda **kw: None)
  os.unlink(f.name)


def progress(filename, percentage, speed, eta, **kw):
  print "%s %s%% @ %s (finished in %s)" % (
    filename, percentage, speed, eta)


def main(argv):
  logging.config.fileConfig(open("logging.ini"))
  path = argv[0]

  files_start = getfiles(path)
  time.sleep(0.1)
  files_end = getfiles(path)

  # Find the files which haven't changed size.
  unchanged = {}
  for filename, start_size in files_start.iteritems():
    try:
      end_size = files_end[filename]
    except KeyError:
      continue

    if start_size == end_size:
      unchanged[filename] = end_size

  logging.info("Found %s files to possibly upload (%s changing)",
      len(unchanged), len(files_end)-len(unchanged))

  # Connect to youtube's SFTP server
  sftp = pexpect.spawn("sftp -oIdentityFile=%s %s@%s" % (
      PRIVATE_KEY, USERNAME.lower(), HOST))
  sftp.expect([PROMPT, SURE])
  logging.info('First line for start %r %r', sftp.before, sftp.after)
  if sftp.after[:5] == SURE[:5]:
    logging.info('Never seen %s before, accepting SSH host key.' % HOST)
    sftp.sendline('yes')
    sftp.expect(PROMPT)

  # open a SFTP channel
  sftp_dirs = []
  for dirname, size in sftp_listdir(sftp, '/').items():
    sftp_dirs.append(dirname)

  for filename, size in unchanged.iteritems():
    # Video files will be gigabytes in size
    #if size < 1e9:
    #  print filename, "File too small", size
    #  continue

    basename = filename[:filename.rfind('.')]
    statusfile = "status-%s.xml" % basename
    successfile = basename+'.uploaded'

    # Has the file already been uploaded?
    if os.path.exists(path+'/'+successfile):
      logging.info("%s is already uploaded and processed.", filename)
      continue

    # Create the directory
    if basename not in sftp_dirs:
      sftp_mkdir(sftp, basename)

    files = {}
    for filename, size in sftp_listdir(sftp, basename).items():
      files[filename] = size

    # Check if the we have a completion status report
    if statusfile in files:
      logging.info("%s already uploaded and processed.", filename)
      if statusfile not in unchanged:
         sftp_get(sftp, basename+'/'+statusfile, path+'/'+statusfile, progress)
      continue

    if "delivery.complete" in files:
      logging.info("%s already uploaded and awaiting processing.", filename)
      continue

    if os.path.exists(path+'/'+statusfile):
      logging.info("%s is already uploaded and waiting status response.", filename)
      continue

    # Upload the actual video
    upload = False
    if filename not in files:
      upload = True

    elif files[filename] != size:
      upload = True

    success = False

    # Create the metadata
    if basename+".xml" not in files:
      datestr = basename[basename.rfind('.')+1:]
      date = time.strptime(datestr, "%Y%m%d-%H%M%S")

      xmlfilename = basename+".xml"

      info = guess_event(date)
      info['date'] = datestr
      info['humandate'] = time.strftime('%A, %d %B %Y', date)
      info['filename'] = filename
      info['username'] = USERNAME
      info['password'] = PASSWORD
      logging.info("Guessing the event is %s", info['shortname'])

      data = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
 xmlns:media="http://search.yahoo.com/mrss"
 xmlns:yt="http://www.youtube.com/schemas/yt/0.2">
 <channel>
   <yt:notification_email>tansell@google.com</yt:notification_email>
   <yt:account>
     <yt:username>%(username)s</yt:username>
     <yt:password>%(password)s</yt:password>
   </yt:account>
   <yt:owner_name>%(username)s</yt:owner_name>

   <item>
     <yt:action>Insert</yt:action>
     <media:title>%(shortname)s - %(date)s</media:title>
     <media:content url="file://%(filename)s" >
       <media:description type="plain">Talk at %(name)s given on %(humandate)s</media:description>
       <media:keywords>open source, google, sydney, %(tags)s</media:keywords>
       <media:category>Science &amp; Technology</media:category>
       <media:rating scheme="urn:simple">nonadult</media:rating>
     </media:content>
     <yt:language>en</yt:language>
     <yt:date_recorded>2005-08-01</yt:date_recorded>

     <yt:location>
       <yt:country>AU</yt:country>
       <yt:zip_code>NSW 2009</yt:zip_code>
       <yt:location_text>Pyrmont</yt:location_text>
     </yt:location>

     <yt:start_time>2007-07-07T07:07:07</yt:start_time> <!-- A date
in the past -->

     <yt:community>
       <yt:allow_comments>Always</yt:allow_comments>
       <yt:allow_responses>Never</yt:allow_responses>
       <yt:allow_ratings>true</yt:allow_ratings>
       <yt:allow_embedding>true</yt:allow_embedding>
     </yt:community>
   </item>
 </channel>
</rss>
""" % info
      f = open(path+"/"+xmlfilename, "w")
      f.write(data)
      f.close()

      logging.debug("XML Metatdata:\n%s", data)
      sftp_write(sftp, basename+'/'+xmlfilename, data)

      logging.info("%s uploaded metadata", xmlfilename)

    if upload:
      logging.info("%s uploading.", filename)
      sftp_put(sftp, path+'/'+filename, basename+'/'+filename, progress)
      logging.info("%s uploaded.", filename)
      success = True
    else:
      success = True

    if success:
      deliveryname = "delivery.complete"

      if deliveryname not in files:
        logging.info("%s uploading completion file", deliveryname)
        sftp_write(sftp, basename+'/'+deliveryname, '')
        logging.info("%s uploading completion file", deliveryname)

      f = open(path+'/'+successfile, 'w')
      f.write(time.time())
      f.write('\n')
      f.close()

  logging.info('Upload done.')


if __name__ == '__main__':
  main(sys.argv[1:])
