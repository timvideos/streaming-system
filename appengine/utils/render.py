

from google.appengine.api import users as appengine_users
from google.appengine.ext.webapp import template

import gravatar

def render(t, kw):
  extra = {
      'appengine_user': appengine_users.get_current_user(),
      'appengine_admin': appengine_users.is_current_user_admin(),
      'appengine_logout_url': appengine_users.create_logout_url('/'),
      }

  # Check people havn't accidently log
  common = set(extra.keys()).intersection(kw.keys())
  if common:
    raise SystemError('The following keys are reserved %s' % common)

  kw.update(extra)
  return template.render(t, kw)
