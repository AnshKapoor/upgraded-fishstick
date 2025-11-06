import logging
import pyqtgraph as pg
from functools import wraps
from typing import *
import threading
import random
import string

MAX_INT32 = 2147483647

F = TypeVar('F', str, int)

_RANDOM_IDENTIFIERS = "#+*!§$%&/()=?"
_RANDOM_IDENTIFIERS += string.ascii_lowercase
_RANDOM_IDENTIFIERS += string.ascii_uppercase
_RANDOM_IDENTIFIERS += string.digits


def random_identifier(length=2):
    return "".join([_RANDOM_IDENTIFIERS[random.randint(0, len(_RANDOM_IDENTIFIERS) - 1)] for _ in range(length)])


def call_async(target, args=None, kwargs=None):
    if args is not None and not isinstance(args, tuple):
        args = (args,)

    if args is None:
        thread = threading.Thread(target=target)
    elif kwargs is None:
        thread = threading.Thread(target=target, args=args)
    else:
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
    thread.start()
    return thread


def get_bit(value: int, start_bit: int, end_bit: Optional[int] = None):
    """
    Extracts a value from an integer between a start and end byte.
    End is optional, one bit value will be extracted if omitted

    examples (tests):
    >>> get_bit(0x10, 4, 7)
    1
    >>> get_bit(0x10, 0, 3)
    0
    >>> bin(get_bit(0x10, 1, 6))
    '0b1000'

    :param value: Integer from which to extract the bits
    :param start_bit: Position of first bit to extract
    :param end_bit: Position of last bit to extract. Interpreted as start_bit if not provided
    :return: Extracted data
    """

    if end_bit is None:
        end_bit = start_bit

    value >>= start_bit
    end_bit -= start_bit

    mask = 1

    for _ in range(end_bit):
        mask <<= 1
        mask += 1

    return value & mask


def iter_unpack_list(message: bytearray, length: int, fmt: F = 'char', unsigned: bool = True,
                     endian: str = '>', length_in_bits: bool = False) -> List[int]:
    """
    Like iter_unpack, only an array of values is unpacked

    :param message: bytearray with the struct data. Will have length*len(fmt) bytes less after func call
    :param length: Amount of values to unpack
    :param fmt: Format of the expected struct data. Either int: num of bytes, str: single character for struct fmt, or
                str: c typedef (char, uchar, long, ...)
    :param unsigned: If True, struct data is interpreted as unsigned, disregarding fmt (except fmt is c type with U)
    :param endian: Endian character, default big endian '>'
    :param length_in_bits: True: length is intepreted as bits, not in bytes
    :return: Array of unpacked struct data
    """
    if length_in_bits:
        length //= 8
    l = []
    for _ in range(length):
        l.append(iter_unpack(message, fmt, unsigned, endian))
    return l


def iter_unpack(message: bytearray, fmt: F = 'char', unsigned: bool = True, endian: str = '>') -> int:
    """
    Unpack and return struct data from bytearray and trim those bytes from the message

    :param message: bytearray with the struct data. Will have len(fmt) bytes less after func call
    :param fmt: Format of the expected struct data. Either int: num of bytes, str: single character for struct fmt, or
                str: c typedef (char, uchar, long, ...)
    :param unsigned: If True, struct data is interpreted as unsigned, disregarding fmt (except fmt is c type with U)
    :param endian: Endian character, default big endian '>'
    :return: Unpacked struct data
    """
    import struct
    formats = {
        1: 'b',
        2: 'h',
        4: 'i',
        8: 'q',
    }

    if isinstance(fmt, int):
        f = formats[fmt]
        l = fmt
    elif isinstance(fmt, str):
        if len(fmt) == 0:
            lengths = {
                'b': 1,
                'h': 2,
                'i': 4,
                'l': 4,
                'q': 8
            }
            fmt = fmt.lower()
            l = lengths[fmt]
            f = fmt
        else:
            if fmt[0].upper() == 'U':
                unsigned = True
                fmt = fmt[1:]
            fmt = fmt.upper().replace(' ', '')
            lengths = {
                'CHAR': 1,
                'SHORT': 2,
                'INT': 4,
                'LONG': 4,
                'LONGLONG': 8
            }
            l = lengths[fmt]
            f = formats[l]
    else:
        raise ValueError
    if unsigned:
        f = f.upper()
    data = struct.unpack(endian + f, bytes(message[0:l]))[0]
    for _ in range(l):
        message.pop(0)
    return data


class Extendable:
    """
    Extensions can be added to this object. Other objects can then
    wait for this instance to load a required extension, afterwards
    initialisation of said object is continued.
    Extensions can also directly extend this objects attributes, by
    an overriden __getattr__
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extensions: List[[object, bool]] = []
        self._extension_listeners: List[[type, Callable[[Optional[object]], None]]] = []

    def get_extension(self, instance: object) -> object:
        """
        Instance wrapper for get_extension_class

        :param instance: The instance of an extension, of whose class there
                         is an instance in this object's extensions
        :return: The instance of instance's class in self.extensions
        """
        return self.get_extension_class(instance.__class__)

    def get_extension_class(self, cls: type) -> Optional[object]:
        """
        Get the instance of cls, which is in self.extensions. If self does not have
        a cls extension, returns None

        :param cls: Any class
        :return: If self has a cls-extension: self's instance of cls. Else None
        """
        for m, _ in self.extensions:
            if m.__class__ == cls:
                return m

    def add_extension_listener(self, instance, listener: Callable[[Optional[object]], None]):
        """
        Wrapper for add_extension_class_listener with instance.__class__

        :param instance: Instance of the class, for which to wait
        :param listener: Listener to call
        """
        return self.add_extension_class_listener(instance.__class__, listener)

    def add_extension_class_listener(self, cls: type, listener: Callable[[Optional[object]], None]):
        """
        Adds listener to self, which is called when anextension of
        class cls is added to self

        :param cls: The ExtensionClass which to wait for
        :param listener: Listener to call when extension is added
        :return:
        """
        m = self.get_extension_class(cls)
        if m is not None:
            Extendable._invoke_listener(listener, m)
            return
        self._extension_listeners.append((cls, listener))

    @staticmethod
    def _invoke_listener(listener: Callable[[Optional[object]], None], extension: object):
        """
        Call a listener for an extension

        :param listener: The function to call
        :param extension: Parameter for listener
        """
        try:
            listener(extension)
        except TypeError:
            listener()

    def has_extension(self, instance: object) -> bool:
        """
        Check if self has an extension of instance's class

        :param instance: Instance of ExtensionClass
        :return: True if self has extension of same class as instance
        """
        return self.has_extension_class(instance.__class__)

    def has_extension_class(self, cls: type) -> bool:
        """
        Check if self has an extension of class cls

        :param cls: ExtensionClass
        :return: True if self has extension of class cls
        """
        return cls in [m.__class__ for m, _ in self.extensions]

    def add_extension(self, instance: object, extend_methods: bool = False):
        """
        Add an extension to this Extendable

        :param instance: The extension to add, as an instance
        :param extend_methods: True of self should gain all (non-private) methods of instance
        """
        self.extensions.append((instance, extend_methods))
        n = 0
        while n != -1:
            i = n = -1
            for cls, listener in self._extension_listeners:
                i += 1
                if instance.__class__ == cls:
                    Extendable._invoke_listener(listener, instance)
                    del self._extension_listeners[i]
                    n = i
                    break

    def __getter(self, item: str) -> Any:
        """
        Call both attribute getters of self for item

        :param item: Name of the attribute to get
        """
        try:
            return object.__getattr__(self, item)
        except AttributeError:
            return object.__getattribute__(self, item)

    def __getattr__(self, item: str) -> Any:
        try:
            r = self.__getter(item)
            return r
        except AttributeError as e:
            if not item.startswith('_'):
                for m, ext in self.extensions:
                    if ext:
                        try:
                            r = object.__getattribute__(m, item)
                            return r
                        except AttributeError:
                            logger.debug("Extension %r does not provide attribute '%s'.", m, item, exc_info=True)
                        except Exception:
                            logger.exception("Failed to access attribute '%s' on extension %r.", item, m)
            raise e


class BColors:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    info = '\033[0m'
    warning = '\033[38;5;3m'
    success = '\033[38;5;2m'
    error = '\033[38;5;1m'
    endc = '\033[0m'


def test_func(exceptions: Optional[List[Exception]] = None, print_done: bool = True, sleep_time: int = 1,
              print_stack: bool = True,
              new_line=True):
    """
    Wrapper for a function in a test environment. Excepts the function to throw any of the exceptions in exceptions,
    and not throw any of exceptions is None

    :param exceptions: List of Exception classes
    :param print_done: If true, "> done." will be printed after execution
    :param sleep_time: Waiting time before execution
    :param print_stack: If wrong exception is thrown, and this flag is set, the stack trace will be printed
    :param new_line: If true, an empty line will be printed after execution
    :return: Returned value of function
    """

    def _test_func(func):
        # noinspection PyTypeChecker
        def _decorator(*args, **kwargs):
            from time import sleep

            exceptions_list = []
            if exceptions is not None:
                exceptions_list = exceptions if isinstance(exceptions, list) else [exceptions]
                if not isinstance(exceptions, list):
                    print(" %s.. (This should cause a %s)" % (func.__doc__.strip(), exceptions.__name__))
                else:
                    print(" %s.. (This should cause one of %s)" % (
                        func.__doc__.strip(),
                        ", ".join([ex.__name__ for ex in exceptions])
                    ))
            else:
                print(" %s.." % func.__doc__.strip())
            sleep(sleep_time)
            success = False
            try:
                value = func(*args, **kwargs)
                success = True
            except Exception as e:
                value = None
                correct = False
                for ex in exceptions_list:
                    if isinstance(e, ex):
                        print(">  Correct Exception. (%s)" % e.__class__.__name__)
                        correct = True
                        continue
                if not correct:
                    print("!> Wrong Exception: (%s)" % e.__class__.__name__)
                    if print_stack:
                        import traceback
                        traceback.print_exc()
                        sleep(.05)

            if exceptions is not None and success:
                print("!> Missing Exception!")
            elif success and print_done:
                print(">  Done.")
            if new_line:
                print('')
            return value

        return wraps(func)(_decorator)

    return _test_func


def str_msg(message: TypeVar('M', bytes, str, Any)):
    """
    Format a message (from SpaceWire for example) to be printed in the log.
    bytes get decoded, newlines get stripped

    :param message: Either bytes, or a to string transformable object
    :return: Formatted string
    """
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    return str(message).strip('\n')


class DefaultMessageHandler:
    """
    MessageHandler which provides warning, error, info and success printing functionality
    """

    @staticmethod
    def warning(message):
        print("%s[Warning]: %s%s" % (BColors.warning, BColors.endc, str_msg(message)))

    @staticmethod
    def error(message):
        print("%s[Error]:   %s%s" % (BColors.error, BColors.endc, str_msg(message)))

    @staticmethod
    def info(message):
        print("%s[Info]:    %s%s" % (BColors.info, BColors.endc, str_msg(message)))

    @staticmethod
    def success(message):
        print("%s[Success]: %s%s" % (BColors.success, BColors.endc, str_msg(message)))


class WrappedMessageHandler:
    """
    Somewhat rudimentary approach to add a 'sender' to log messages at constructor level
    """

    def __init__(self, message_handler, sender, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if message_handler is None:
            message_handler = DefaultMessageHandler()
        self.message_handler = message_handler
        self.sender = sender

    def warning(self, message):
        self.message_handler.warning("%s: %s" % (self.sender, str_msg(message)))

    def error(self, message):
        self.message_handler.error("%s: %s" % (self.sender, str_msg(message)))

    def info(self, message):
        self.message_handler.info("%s: %s" % (self.sender, str_msg(message)))

    def success(self, message):
        self.message_handler.success("%s: %s" % (self.sender, str_msg(message)))


def add_value_to_data(data: Dict[str, List[float]], value, offset=1.0, history=10):
    """
    Adds a new value to a data object which looks like
    {
     'x': [1.0, 1.2, 1.2],
     'y': [0.0, 0.1, 0.2]
    }

    :param data: Dictonary with data points
    :param value: New (y-axis) value
    :param offset: Time between the last data point and the new one
    :param history: Amount of data points stored as history
    """
    for i in range(0, len(data["x"])):
        data["x"][i] = offset * i

    while len(data["x"]) > 0 and data["x"][-1] + offset > history:
        del data["x"][-1]
        del data["y"][0]

    data["y"].append(value)
    try:
        data["x"].append(data["x"][-1] + offset)
    except IndexError:
        data["x"].append(0)

    for i in range(0, len(data["x"])):
        data["x"][i] -= data["x"][-1]
logger = logging.getLogger(__name__)

