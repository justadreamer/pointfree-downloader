from http.cookiejar import MozillaCookieJar
from http.cookiejar import LoadError

def tryFixCookieFile(filename):
    print("Trying to fix cookie file")
    f = open(filename)
    lines = ['# Netscape HTTP Cookie File\n']
    for l in f:
        lines.append(l)
    f.close()

    f = open(filename,'w')
    for l in lines:
        print(l,file=f,end='')
    f.close()

def tryLoadCookies(cookies: MozillaCookieJar):
    try:
        cookies.load(ignore_expires=True)
        for cookie in cookies:
            cookie.expires = 3107626352
        return True
    except LoadError:
        print("Cookie has incorrect format, must have comment containing # Netscape on the top")
    return False

def loadCookies(filename):
    cookies = MozillaCookieJar(filename=filename)
    if not tryLoadCookies(cookies):
        tryFixCookieFile(filename)
        tryLoadCookies(cookies)
    return cookies