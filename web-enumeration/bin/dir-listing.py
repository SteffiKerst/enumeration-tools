# Directory listing tool
# Can be used alone or as a module

# Dependencie lists:
# ***request
from requests import get
from queue import Queue
from os.path import join
from threading import Thread
from time import sleep
# Handler for the directory listing session
class gobuster:
    def __init__(self, url:str, simple_atuh_username, simple_auth_password, wordlist:iter, threads:int, success_codes:iter, file_extensions:iter, io_object, verbose:bool, ignore_errors:bool, only_extensions:bool):
        self.__url = url
        # Usename and password provided for simple http oauth
        # If one is false no one is going to be used
        if type(simple_atuh_username) == str and type(simple_auth_password) == str:
            self.__headers = {'username':simple_atuh_username, 'password':simple_auth_password}
        else:
            # when no one or the user do not put one ignore the auth
            self.__headers  = None
        # Wordlist that is going to be used to brute force each word (one per line against target)
        self.__wordlist = wordlist
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
        # Variable to ignore error messages
        self.__ignore_errors = ignore_errors
        # When this is set to true (enabled) the script is not going to use the raw word, but it is going to use it merged with the extension
        # provided
        self.__only_extensions = only_extensions

        # Values to get the total percentage of done threads
        self.__extensions_length = len(file_extensions)
        self.wordlist_length = len(wordlist)
        self.wordlist_multiplier = 1 if self.__extensions_length <= 0 else self.__extensions_length
        # Queue to handler results of everything
        # Use this organize all outputs because threads attenpt to in random orders
        self.__print_queue = Queue()
        # Reference to check active active threads
        self.__active_threads = 0
        # Handler to print the percentage
        self.finished_threads = 0
    # Download the page and return it's status code
    def downloadPage(self, url):
        # Try and except here because sometimes it
        try:
            return get(url,headers=self.__headers).status_code
        except Exception as e:
            if self.__verbose and not self.__ignore_errors:
                self.__print_queue.put(f"Timeout {url}")
    # Each processed word of the wordlist at some time are going to be initialized as threads
    def wordHandler(self, word):
        # Merge the url with the work and send it to download page function
        status_code = self.downloadPage(join(self.__url, word).replace('\\', '/'))
        if status_code in self.__success_codes:
            if self.__verbose:
                self.__print_queue.put(f"{word} {status_code}")
        # When finish remove this thread from active threads
        self.__active_threads -= 1
        # This thread finish so add it to finished threads
        self.finished_threads += 1
        # Finally kill the thread
        exit(-1)
    # simpler function to start threads in one call
    def threadStarter(self, word):
        # Wait until a free port is open for this thread
        while self.__active_threads >= self.__max_threads:
            pass
        # Start the thread
        Thread(target=self.wordHandler, args=([word])).start()
        # Add the thread to  the pool
        self.__active_threads += 1
    # Print the status of the queue
    def queuePrinter(self):
        while self.finished_threads < (self.wordlist_length * self.wordlist_multiplier):
            print(self.__print_queue.get())
            # Print the percentage of completed
            print(f"{self.finished_threads}/{self.wordlist_length} {(self.finished_threads * self.wordlist_multiplier)/self.wordlist_length}", end='\r')
        print("-DONE-")
    # Function to start listing
    def start(self):
        try:

            if self.__verbose:
                Thread(target=self.queuePrinter,).start()
            for word in self.__wordlist:
                word = word.strip()
                # check also for the raw word
                if not self.__only_extensions:
                    self.threadStarter(word)
                # for each extension create a new thread with the word + .extension
                for extension in self.__file_extensions:
                    self.threadStarter(f'{word}.{extension.replace(".", "")}')
            # Wait until lasts threads finish
            while self.__active_threads > 0:
                pass
        except KeyboardInterrupt:
            # This kills the queuePrinter function
            self.finished_threads = (self.wordlist_length * self.wordlist_multiplier)
            # Wait until the function read the variable
            sleep(2)
            exit(-1)
g = gobuster('https://www.ford.com/', False, False, open('./../../thirdparty/wordlists/directory/directory-list-2.3-medium.txt').readlines(), 100, [200, 303], ['html', 'php', 'txt'], 2,1,1,1)
g.start()