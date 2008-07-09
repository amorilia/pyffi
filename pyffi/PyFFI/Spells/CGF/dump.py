# dump contents of file to screen

def testFile(stream,
             version = None, user_version = None,
             filetype = None, chunks = None, versions = None, **kwargs):
    for i, (chunk, version) in enumerate(zip(chunks, versions)):
        print 'chunk %3i (%s version 0x%04X)'%(i, chunk.__class__.__name__,version)
        print chunk
