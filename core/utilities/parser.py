import stringcase

from core.models.base.parser import parser as parser_


def get_output_filename(parser: parser_.Parser) -> str:
    if parser.OUTPUT_FILE is not None:
        return parser.OUTPUT_FILE
    return stringcase.snakecase(parser.__class__.__name__) + '.xlsx'


def get_remains_delay(delay, start_time, end_time):
    elapsed_time = end_time - start_time
    return max(delay - elapsed_time, 0)
