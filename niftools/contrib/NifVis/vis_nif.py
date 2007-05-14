from NifFormat.NifFormat import NifFormat

import inspect

TypeRegistry = {}
BlockRegistry = []
Version = 0
UserVersion = 0

#
# A simple custom exception class.
#
class NIFImportError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def LoadNif( filename ):
    global Version, UserVersion
    try:
        print "Reading Nif: %s" % filename
        f = open( filename, "rb" )
        Version, UserVersion = NifFormat.getVersion( f )
        if Version >= 0:
                print "( Version 0x%08X )" % Version
                root_blocks = NifFormat.read( Version, UserVersion, f, verbose = 0 )
                for block in root_blocks:
                    AddBlock( block )
        elif Version == -1:
            raise NIFImportError( "Unsupported NIF version." )
        else:
            raise NIFImportError( "Not a NIF file." )
    
    except NIFImportError, e: # in that case, we raise a menu instead of an exception
        print 'NIFImportError: ' + e.value
        return



def AddBlock( block ):
    global Version, UserVersion
    
    if not block: return
    
    if not TypeRegistry.has_key( type( block ).__name__ ):
        TypeRegistry[type( block ).__name__] = []
    
    TypeRegistry[type( block ).__name__].append( block )
    BlockRegistry.append( block )
    
    for child in block.getLinks( Version, UserVersion ):
        if not child in BlockRegistry: AddBlock( child )
