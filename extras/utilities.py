import sys
import os
import urllib2

from django.conf import settings


HEADERS = {
    'User-Agent': 'urllib2 (Python %s)' % sys.version.split()[0],
    'Connection': 'close',
}


def get_favicon(url, path='favicon.ico', alt_icon_path='alticon.ico'):

    if not url.endswith('/'):
        url += '/'

    request = urllib2.Request(url + 'favicon.ico', headers=HEADERS)
    try:
	    icon = urllib2.urlopen(request).read()
    except(urllib2.HTTPError, urllib2.URLError):
	    return
		
    open(path, 'wb').write(icon)	
    rel_path = url + 'favicon.ico'
    return rel_path



def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)
## end of http://code.activestate.com/recipes/82465/ }}}

def unique_slug(item,slug_source,slug_field):
    if not getattr(item, slug_field): # if it's already got a slug, do nothing.
        from django.template.defaultfilters import slugify
        slug = slugify(getattr(item,slug_source))
        itemModel = item.__class__
        # the following gets all existing slug values
        allSlugs = [sl.values()[0] for sl in itemModel.objects.values(slug_field)]
        if slug in allSlugs:
            import re
            counterFinder = re.compile(r'-\d+$')
            counter = 2
            slug = "%s-%i" % (slug, counter)
            while slug in allSlugs:
                slug = re.sub(counterFinder,"-%i" % counter, slug)
                counter += 1
        setattr(item,slug_field,slug)
