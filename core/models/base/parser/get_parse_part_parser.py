import abc

from core.models.base.parser import part_parser


class GetParsePartParser(part_parser.PartParser, abc.ABC):
    def find_one_part(self, part):
        html = self.get_part_html(part)
        if html is None:
            return part.not_found()
        ready_part = self.parse_html(html, part)
        return ready_part

    @staticmethod
    @abc.abstractmethod
    def get_part_html(part):
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_html(html, part):
        pass
