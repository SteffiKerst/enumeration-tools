# Directory listing tool
# Can be used alone or as a module

# Dependencie lists:
# ***request
from requests import get
from queue import Queue
from os.path import join
from threading import Thread
# Handler for the directory listing session
class gobuster:
    def __init__(self, url:str, simple_atuh_username, simple_auth_password, wordlists_path:str, threads:int, success_codes:iter, file_extensions:iter, io_object, verbose:bool, only_extensions:bool):
        self.__url = url
        # Usename and password provided for simple http oauth
        # If one is false no one is going to be used
        if type(simple_atuh_username) == str and type(simple_auth_password) == str:
            self.__headers = {'username':simple_atuh_username, 'password':simple_auth_password}
        else:
            # when no one or the user do not put one ignore the auth
            self.__headers  = None
        # Wordlists that is going to be used to brute force each word (one per line against target)
        self.__wordlists_path = wordlists_path
        # The maximum number of threads active at the same time
        self.__max_threads = threads
        # If the requests results with a code in the success codes it's going to be printed
        self.__success_codes = success_codes
        # This are the file extension that are going to be add to each work in the wordlist; if only_extension is disabled
        # it also going to use the raw word
        self.__file_extensions = file_extensions
        # File like object to write to useful for module like usage if the script is used as a module a io is required
        # when the script is used as a program it automatically open a path provided by used to  a io object (open the file path)
        self.__io = io_object
        # If false do not print operations
        self.__verbose = verbose
        # When this is set to true (enabled) the script is not going to use the raw word, but it is going to use it merged with the extension
        # provided
        self.__only_extensions = only_extensions

        # Queue to handler results of everything
        # Use this organize all outputs because threads attenpt to in random orders
        self.__print_queue = Queue()
        # Reference to check active active threads
        self.__active_threads = 0

    # Download the page and return it's status code
    def downloadPage(self, url):
        # Try and except here because sometimes it
        try:
            return get(url,headers=self.__headers).status_code in self.__success_codes
        except Exception as e:
            if self.__verbose:
                self.__print_queue.put(e)
    # Each processed word of the wordlist at some time are going to be initialized as threads
    def wordHandler(self, word):
        # Merge the url with the work and send it to download page function
        status_code = self.downloadPage(join(self.__url, word))
        if status_code:
            if self.__verbose:
                self.__print_queue.put(f"{word} {status_code}")
g = gobuster('https://wikipedia.org', False, False, './../../thirdparty/wordlists/directory/directory-list-2.3-medium.txt', 10, [123,123,123], [], 2,1,1)
g.downloadPage('https://wikipedia.org')