import abc

from core.models.base.parser import part_parser


class GetParsePartParser(part_parser.PartParser, abc.ABC):
    def find_one_part(self, part):
        with self.get_part_html(part) as html:
            if html is None:
                return part.not_found()
            with self.parse_html(html, part) as ready_path:
                return ready_part

    @staticmethod
    @abc.abstractmethod
    def get_part_html(part):
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_html(html, part):
        pass
