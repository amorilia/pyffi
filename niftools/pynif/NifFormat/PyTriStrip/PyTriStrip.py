from TraversalUtilities import Stripifier
from Mesh import Mesh

def generateFaces(indices, is_strip = False):
    """A generator for iterating over the faces in a list of triangles
    or in a strip. Degenerate triangles in strips are discarded.
    
    >>> [i for i in generateFaces([1, 0, 1, 2, 3, 4, 5, 6], is_strip = True)]
    [(0, 1, 2), (1, 3, 2), (2, 3, 4), (3, 5, 4), (4, 5, 6)]
    >>> [i for i in generateFaces([0, 1, 2, 3, 4, 5, 6, 7, 8], is_strip = False)]
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]"""
    i = indices.__iter__()
    if not is_strip:
        while True:
            yield (i.next(), i.next(), i.next())
    else:
        j = True
        t1 = i.next()
        t2 = i.next()
        while True:
            t0 = t1
            t1 = t2
            t2 = i.next()
            if t0 == t1 or t1 == t2 or t2 == t0: continue
            if j:
                yield (t0, t1, t2)
            else:
                yield (t0, t2, t1)
            j = not j

def getStrips(triangles):
    """Converts triangles into strips.

    Returns a tuple (triangles, fans, strips) where triangles is a
    list of triangle indices, fans is a list of fans, and strips is a
    list of strips. A fan is also a list of triangle indices, and so
    is a strip.

    (Note: in the current implementation, fans is always [].)

    >>> triangles = [1, 5, 2, 5, 2, 6, 5, 9, 6, 9, 6, 10, 9, 13, 10, 13, 10, 14, 0, 4, 1, 4, 1, 5, 4, 8, 5, 8, 5, 9, 8, 12, 9, 12, 9, 13, 2, 6, 3, 6, 3, 7, 6, 10, 7, 10, 7, 11, 10, 14, 11, 14, 11, 15]
    >>> getStrips(triangles)
    ([], [], [[1, 0, 1, 4, 5, 8, 9, 12, 13], [2, 1, 2, 5, 6, 9, 10, 13, 14], [3, 2, 3, 6, 7, 10, 11, 14, 15]])
    """

    # build a mesh from triangles
    mesh = Mesh()
    for face in generateFaces(triangles):
        mesh.AddFace(*face)

    # return the strip
    stripifier = Stripifier()
    stripifier(mesh)
    return stripifier.TriangleList, stripifier.TriangleFans, stripifier.TriangleStrips

if __name__=='__main__':
    import doctest
    doctest.testmod()
    
