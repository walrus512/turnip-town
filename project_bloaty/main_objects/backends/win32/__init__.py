#
backend_list = []

try:
    import player_pymedia
    backend_list.append('backends.win32.player_pymedia')
except Exception, expt:
    print str(Exception) + str(expt)
    
try:
    import player_null
    backend_list.append('backends.win32.player_null')
except Exception, expt:
    print str(Exception) + str(expt)
    
#module_names = ['player_pymedia', 'player_true']
#modules = map(__import__, module_names) 