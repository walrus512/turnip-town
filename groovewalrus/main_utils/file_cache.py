
import hashlib
import os

# max number of cached files
CACHE_LIMIT = 30
ENCODING = 'utf-8'

def CreateCachedFilename(cache_path, file_string):
    """ Checks if file exists, returns new file name if it doesn't. """
    
    # lets make file names as hex strings for something to do
    hex_file_name = hashlib.md5(file_string).hexdigest()
    full_file_path = cache_path.replace("\\", os.sep) + os.sep + hex_file_name + '.mp3'
    if os.path.isfile(full_file_path):
        return (full_file_path, True)
    else:
        return (full_file_path, False)

def CheckCache(cache_path):
    """ Checks if cache limit has been reached, removes oldest if it has. """
    
    file_path = cache_path.replace("\\", os.sep)
    file_list = os.listdir(file_path)
    
    first_modified = 2000000000
    oldest_file = ''
    
    if len(file_list) > CACHE_LIMIT:
        
        for file_name in objects:
        # find oldest file
            full_file_path = file_path + os.sep + file_name
            modified = os.path.getmtime(full_file_path)
            if modified < first_modified:
                    first_modified = modified
                    oldest_file = full_file_path
        
        # remove oldest file
        os.remove(oldest_file)
        #print oldest_file
