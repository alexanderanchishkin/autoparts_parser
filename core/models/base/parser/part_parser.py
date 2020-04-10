import abc
import re
import requests
from config import settings
import time
import traceback

from core.io.database.utilities.part import write_parts
from core.models.base.parser import parser
from core.models.part import Part

from multiprocessing import dummy as thread


class PartParser(parser.Parser, abc.ABC):
    MULTI_REQUEST = False
    THREADS_COUNT = 0

    def find_parts(self, parts):
        # TODO: Realize
        pass

    @abc.abstractmethod
    def find_one_part(self, part):
        pass
