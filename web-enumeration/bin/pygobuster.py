# Directory listing tool
# Can be used alone or as a module

# Dependencie lists:
# ***request
from requests import get
from queue import Queue
from os.path import join
from threading import Thread
from time import sleep
from argparse import ArgumentParser

# Class when no output was provided
class NoOutput:
    def close(self):
        pass
    def write(self, value):
        pass
    def flush(self):
        pass
# Handler for the directory listing session
class GoBuster:
    def __init__(self, url: str, simple_atuh_username, simple_auth_password, usergent:str, cookies:str, wordlist: iter, threads: int,
                 success_codes: iter, file_extensions: iter, io_object, verbose: bool, ignore_errors: bool,
                 only_extensions: bool):
        self.__url = url
        # Usename and password provided for simple http oauth
        # If one is false no one is going to be used
        if simple_atuh_username:
            self.__headers = {'username': simple_atuh_username}
        else:
            # when no one or the user do not put one ignore the auth
            self.__headers = {}
        if simple_auth_password:
            self.__headers['password'] = simple_auth_password
        # user agent to make requests
        self.__headers['User-Agent'] = usergent
        # Cookies for the request
        self.__cookies = dict(cookies_are=cookies)
        # Wordlist that is going to be used to brute force each word (one per line against target)
        self.__wordlist = wordlist
        # The maximum number of threads active at the same time
        self.__max_threads = threads
        # If the requests results with a code in the success codes it's going to be printed
        self.__success_codes = success_codes
        # This are the file extension that are going to be add to each work in the wordlist; if only_extension is
        # disabled it also going to use the raw word
        self.__file_extensions = file_extensions
        # File like object to write to useful for module like usage if the script is used as a module a io is required
        # when the script is used as a program it automatically open a path provided by used to  a io
        # object (open the file path)
        self.__io = io_object
        # If false do not print operations
        self.__verbose = verbose
        # Variable to ignore error messages
        self.__ignore_errors = ignore_errors
        # When this is set to true (enabled) the script is not going to use the raw word, but it is going to use it
        # merged with the extension
        # provided
        self.__only_extensions = only_extensions

        # Values to get the total percentage of done threads
        self.__extensions_length = len(file_extensions)
        self.wordlist_length = len(wordlist)
        self.wordlist_multiplier = 1 if self.__extensions_length <= 0 else self.__extensions_length
        self.totalThreads = (self.wordlist_length * self.wordlist_multiplier)
        # Queue to handler results of everything
        # Use this organize all outputs because threads attenpt to in random orders
        self.__print_queue = Queue()
        # Queue to handler all writing stuff in the main thread
        self.__write_queue = Queue()
        # Reference to check active active threads
        self.__active_threads = 0
        # Handler to print the percentage
        self.finished_threads = 0
    # Download the page and return it's status code
    def downloadPage(self, url):
        # Try and except here because sometimes it
        # noinspection PyBroadException
        try:
            return get(url, headers=self.__headers, cookies=self.__cookies).status_code
        except:
            if self.__verbose:
                if not self.__ignore_errors:
                    self.__print_queue.put(f"Timeout {url}")

    # Each processed word of the wordlist at some time are going to be initialized as threads
    def wordHandler(self, word):
        # Merge the url with the work and send it to download page function
        status_code = self.downloadPage(join(self.__url, word).replace('\\', '/'))
        if status_code in self.__success_codes:
            if self.__verbose:
                self.__print_queue.put(f"{word} {status_code}")
            # Add the value to the writing queue
            self.__write_queue.put(f"{word} {status_code}")
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
    # Write results to target
    def queueWriter(self):
        while self.finished_threads < self.totalThreads:
            value = self.__write_queue.get()
            self.__io.write(value+'\n')
            # Save changes inmediatly
            self.__io.flush()
        self.__io.close()
    # Print the status of the queue
    def queuePrinter(self):
        while self.finished_threads < self.totalThreads:
            print(self.__print_queue.get())
            # Print the percentage of completed
            print(
                f"{self.finished_threads}/{self.wordlist_length} "
                f"{(self.finished_threads * self.wordlist_multiplier)/self.wordlist_length}",
                end='\r')
        print("-DONE-")

    # Function to start listing
    def start(self):
        try:
            # If verbose mode is active
            if self.__verbose:
                Thread(target=self.queuePrinter, ).start()
            Thread(target=self.queueWriter, ).start()
            for word in self.__wordlist:
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
# Process the arguments
# Only when is used as a script
def processArgs(args):
    try:
        args['o'] = open(args['o'], 'w')
    except Exception as e:
        args['o'] = NoOutput()
    try:
        with open(args['wordlist'], 'r') as file:
            args['wordlist'] = tuple(map(lambda word: word.strip(), file.readlines()))
            file.close()
    except:
        exit(-1)
    args['x'] = args['x'].split(',')
    args['s'] = args['s'].split(',')
    return args
# main function to execute it as program
def main():
    parser = ArgumentParser()
    parser.add_argument('-u', '--url', help='Target url', required=True)
    parser.add_argument('-U', help='Username for simple oauth', default=False)
    parser.add_argument('-P', help='Password for simple oauth', default=False)
    parser.add_argument('-a', help='User-Agent for requests default is pygobuster', default='pygobuster')
    parser.add_argument('-c', help='Cookies for the requests', default='')
    parser.add_argument('-w', '--wordlist', help='File path to the wordlist', required=True)
    parser.add_argument('-t', help='Number of threads to be active during the session', type=int, default=10)
    parser.add_argument('-s', help='Status codes (separated by commas ",")to be used by default 200,204,301,302,307,403', default='200,204,301,302,307,403')
    parser.add_argument('-x', help='File extensions to search for. (separated by commas ",")', default='')
    parser.add_argument('-o', help='Output file', default=False)
    parser.add_argument('-v', help='Verbose mode, print all outputs', default=False, action='store_const', const=True)
    parser.add_argument('--ignore-errors', help='Ignore error  messages needs verbose to work', default=False, action='store_const', const=True)
    parser.add_argument('--only-extension', help='Do not  search for folder, only for files with extensions (require extensions)', default=False, action='store_const', const=True)
    args = processArgs(vars(parser.parse_args()))
    # Extract keys
    values = args.values()
    buster = GoBuster(*values)
    buster.start()
# When the script is running individualy
# else it works as a module
if __name__ == '__main__':
    main()