# Based on example code from:
#   http://en.gravatar.com/site/implement/images/python/

import urllib, hashlib

from django.template.defaultfilters import stringfilter, register

@register.filter
@stringfilter
def gravatar(email, size=40):
  default = "http://sydney-linux-user-group.appspot.com/images/silhouette.png"

  # construct the url
  gravatar_url = "http://www.gravatar.com/avatar/"
  gravatar_url += hashlib.md5(email.lower().strip()).hexdigest()
  gravatar_url += "?"
  gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
  return gravatar_url
