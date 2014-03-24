import struct
import os


def requires_open(func):
    def wraps(*args, **kwargs):
        self = args[0]
        if not self.is_open():
            raise IOError("PostingsFile is not open.")
        return func(*args, **kwargs)
    return wraps


class PostingsFile(object):
    """
    Abstracts I/O logic for reading and writing to the postings file.

    The postings file is an unstructuted collection of records. Individual
    records are identified and accessed by looking up a dictionary (stored
    separately).

    If a record is longer than a DWord, it must be length-prefixed. The prefix
    is an unsigned DWord, which limits the size of a record to 2 ** 32 fields.

    Fields are big-endian.

    The following record types are supported:
    - Arrays of (doc_id, term_freq)-tuples
    """
    DWORD_SIZE = 4
    DWORD_FMT = '>I'

    def __init__(self, filename, filemode):
        assert type(filename) == str
        assert type(filemode) == str

        self.__filename = filename
        self.__file_mode = filemode
        self.__fd = None

    def __del__(self):
        self.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        if not self.__fd:
            self.__fd = open(self.__filename, self.__file_mode)

    def close(self):
        if self.__fd:
            self.__fd.close()
            self.__fd = None

    # Returns True iff the PostingsFile is open.
    def is_open(self):
        return bool(self.__fd)

# API for reading/writing abstract data structures
###############################################################################
    @requires_open
    def write_idtf_array(self, array):
        """
        Writes an array of (doc_id, term_frequency)-tuples.
        """
        assert array and type(array) == list

        self.__fd.seek(0, os.SEEK_END)
        position = self.__fd.tell()

        self.__write_prefix(len(array))
        for item in array:
            assert type(item) == tuple
            assert len(item) == 2

            self.__write_idtf_tuple(item)

        return position

    @requires_open
    def read_idtf_array(self, offset):
        """
        Reads an array of (doc_id, term_frequency)-tuples.
        """
        assert type(offset) == int and offset >= 0

        result = list()
        self.__fd.seek(offset)

        count = self.__read_prefix()
        for i in range(count):
            result.append(self.__read_idtf_tuple())

        return result

# Private methods for reading/writing basic data types
###############################################################################
    @requires_open
    def __write_DWord(self, dword):
        byte_array = struct.pack(PostingsFile.DWORD_FMT, int(dword))
        self.__fd.write(byte_array)
        return self.__fd.tell()

    @requires_open
    def __read_DWord(self):
        byte_array = self.__fd.read(PostingsFile.DWORD_SIZE)
        result = struct.unpack(PostingsFile.DWORD_FMT, byte_array)[0]

        return result

    @requires_open
    def __write_prefix(self, value):
        assert type(value) == int and value >= 0
        self.__write_DWord(value)

    @requires_open
    def __read_prefix(self):
        length = self.__read_DWord()
        assert length > 0

        return length

# Private methods for reading/writing compound data types
###############################################################################
    @requires_open
    def __write_idtf_tuple(self, _tuple):
        assert len(_tuple) == 2

        cur = self.__fd.tell()
        self.__write_DWord(_tuple[0])
        effect = self.__write_DWord(_tuple[1])

        assert effect - cur == 2 * PostingsFile.DWORD_SIZE

    @requires_open
    def __read_idtf_tuple(self):
        result = (self.__read_DWord(), self.__read_DWord())

        return result
