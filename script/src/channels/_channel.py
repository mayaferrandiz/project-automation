from script.src.config import Config
from script.src.templates.processor import TemplateProcessor
from script.src.utils import setup_logging


class Channel:
    def __init__(self, name, class_name, content_type, config: Config) -> None:
        self.config = config
        self.class_name = class_name
        self.tp = TemplateProcessor(config, content_type)
        self.logger = setup_logging(name)