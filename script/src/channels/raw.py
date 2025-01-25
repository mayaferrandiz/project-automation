import shutil

from script.src.channels._channel import Channel
from script.src.config import Config
from script.src.constants import MEDIA
from script.src.utils import get_media_files, get_project_path


class RawHandler(Channel):
    def __init__(self, config: Config):
        init = {
            'name': __name__,
            'class_name':self.__class__.__name__,
            'config': config
        }
            
        super().__init__(**init)

        self.media = MEDIA

    def publish(self, name: str) -> None:        
        try:

            self.delete(name)

            project_dir = get_project_path(self, name)
            output_dir = self.config.base_dir / '_output' / name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(project_dir / 'content/README.md', output_dir / 'README.md')
            shutil.copy2(project_dir / 'content/content.md', output_dir / 'content.md')

            for media_type in self.media:
                media_files = get_media_files(self, name, media_type, self.media[media_type])
                for file in media_files:
                    shutil.copy2(file, str(output_dir / file.name))
                
            self.logger.info(f"Published raw content at {output_dir}")
        except Exception as e:
            self.logger.error(f"Error publishing raw: {e}")
            raise

    def delete(self, name: str) -> None:
        try:
            output_dir = self.config.base_dir / '_output' / name

            if output_dir.exists():
                shutil.rmtree(output_dir)
        except Exception as e:
            self.logger.error(f"Error publishing raw: {e}")
            raise