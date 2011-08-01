#!/usr/bin/env python

"""
the main function in this module is sendSMS, which sends an SMS message
using txtlocal
"""

import urllib
import string
import re

from cmdashboard import settings

def sendSMS( numbers, message, username=settings.SMSUSER, password=settings.SMSPASS,
             proxy = None,
             allowLongMsg = False,
             sender = settings.SMSSENDER,
             **kwargs ):

    """
    Send an SMS message

    Arguments to function are as follows:

        numbers: List or phone numbers, or a single phone number.
                  Each phone number should be an international phone number.
                  Note that as per the API this should only contain digits
                  and not other characters.
                  The API specifies a comma-separated list, but for convenience
                  this function will also accept a list or tuple in python,
                  and convert it accordingly.
        message: The message
        username: username on txtlocal.co.uk
        password: password on txtlocal.co.uk

    Optional arguments:

        proxy: the proxy URL needed to connect to the internet at the client
               end, e.g. 'http://my.site.proxy:8080'

        allowLongMsg: set to True to allow long message, otherwise messages
                      will be truncated at 160 chars

        sender: sender name

        anything else: will be passed as-is to the HTTP interface,
                       as documented on the txtlocal website,
                       for example:  rcpurl=...

    All arguments (or each phone number in the list) should be of type
    string, except that integers are accepted and are converted into strings
    """

    # build up dictionary of args
    dict = _getArgsDict(numbers, message, username, password,
                        sender, allowLongMsg, kwargs)
    
    # URL-encode this (note urlencode will accept ints or strings)
    data = urllib.urlencode(dict)

    # and post
    url = "http://www.txtlocal.com/sendsmspost.php"
    response = _postURL(url, data, proxy)
    
    # check if it seemed to work
    if not _checkResponse(response):
        raise RuntimeError("Message may not have been sent. " +
                           "Response was: '%s'" % response)

def _makeSender(sender):
    """
    Make an acceptable sender line, else return an empty string
    """
    s = ""
    for char in sender:
        if char.isalnum() or char == " ":
            s += char
    s = s[:11]
    if len(s) < 3:
        return ""
    else:
        return s    

    
def _getArgsDict(numbers, message, username, password, sender, allowLongMsg,
                 kwargs):
    """
    Helper function for sendSMS - makes dictionary of args according to the
    API
    """
    dict = {}
    if isinstance(numbers, list) or isinstance(numbers, tuple):

        numbers = map(lambda x: "%s" % x, numbers)  # convert any ints to
                                                    # strings
                                                    
        numbers = string.join(numbers, ",")  # and turn into comma separated

    dict['selectednums'] = numbers

    if not allowLongMsg:
        message = message[:160]    

    dict['message'] = message

    dict['uname'] = username
    dict['pword'] = password

    # any additional args
    for key in kwargs.keys():
        dict[key] = kwargs[key]
    
    if sender:
        dict['from'] = _makeSender(sender)

    dict['info'] = 1  # always request info, so we can parse the response
    return dict


def _postURL(url, data, proxy):
    """
    Helper function for sendSMS - posts request and returns response
    """
    if proxy:
        proxies = { 'http': proxy }
    else:
        proxies = None
    filehandle = urllib.urlopen(url, data = data, proxies = proxies)
    response = string.join(filehandle.readlines(), "\n")
    return response


def _checkResponse(response):
    """
    Helper function for sendSMS - check response text (string) to see if the
    SMS appears to have been sent - returns True or False

    This is a basic sanity check and doesn't guarantee delivery.  Checks that
    the report contains some believable numbers regarding credits.
    """
    try:
        credAvail = _parseToken(response,"CreditsAvailable")
        credReq = _parseToken(response,"CreditsRequired")
        credRem = _parseToken(response,"CreditsRemaining")
    except:
        return False

    return (credReq > 0 and credAvail - credReq == credRem)

    
def _parseToken(response, token):
    """
    Helper function for _checkResponse: look for numeric value in response
    with a given token name
    """
    regexp = token + "=([0-9]+)"
    return string.atoi(re.search(regexp, response).group(1))


#-----------------------------------
# Main program example calling code

if __name__ == '__main__':

    numbers = ('447000000000', '447000000001')
    username = 'my_username@example.com'
    password = 'my_password'
    proxy = 'http://mysite.:8080'

    message = "Here's a test message, and a very fine test message it is too."
    
    sendSMS( numbers, message, username, password )
