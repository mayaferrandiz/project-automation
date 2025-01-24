
from script.src.config import Config
from script.src.file import FileHandler
from script.src.github import GithubHandler
from script.src.jekyll import JekyllHandler
from script.src.pdf import PDFHandler
from script.src.things import ThingsHandler
from script.src.utils import (
    get_project_directories,
    get_project_metadata,
    setup_logging,
)


class Automation:

    def __init__(self, config: Config):
        self.config = config
        self.github = GithubHandler(config)
        self.jekyll = JekyllHandler(config)
        self.things = ThingsHandler(config)
        self.files = FileHandler(config)
        self.pdf = PDFHandler(config)
        self.logger = setup_logging(__name__)

    def publish_all(self) -> None:
        self.stage_all_projects()

        projects = get_project_directories(self)
        for project_dir, name in projects:
            self.github.publish(name)
        
        self.jekyll.stage_roadmap()
        self.jekyll.publish()

    def publish_website(self) -> None:
        self.jekyll.publish()

    def publish_project(self, name: str) -> None:
        self.stage_project(name)

        self.github.publish(name)

        self.jekyll.stage_roadmap()
        self.jekyll.publish()

    def stage_project(self, name: str) -> None:
        self.github.stage_readme(name)
        self.jekyll.stage_post(name)                    
        self.jekyll.stage_media(name)
        self.pdf.create(name)

    def stage_all_projects(self) -> None:
        projects = get_project_directories(self)
        for project_dir, name in projects:
            self.stage_project(name)

    def create_project(self, name: str, display_name: str) -> None:
        self.files.create(name, display_name)
        self.github.create(name)
        self.things.create(display_name)
        self.pdf.create(name)
        self.publish_project(name)
    
    def list_projects(self) -> None:
        """List all projects with their details"""
        projects = get_project_directories(self)
        
        if not projects:
            self.logger.info("No projects found")
            return
            
        self.logger.info(f"\n -- Found {len(projects)} projects: --")
        for project_dir, name in sorted(projects):
            try:
                metadata = get_project_metadata(self, name)
                display_name = metadata['project']['display_name']
                date = metadata['project']['date_created']
                status = metadata['project']['status']
                self.logger.info(f"{display_name} ({name}); Created: {date}; Status: {status}")
            except Exception as e:
                self.logger.error(f"Error reading project {name}: {e}")

    def rename_project(self, old_name: str, new_name: str, new_display_name: str) -> None:
        """Rename a project locally and on GitHub"""        
        old_path = self.config.base_dir / old_name
        new_path = self.config.base_dir / new_name
        
        if not old_path.exists():
            raise ValueError(f"Project {old_name} not found")
        if new_path.exists():
            raise ValueError(f"Project {new_name} already exists")
            
        try:
            
            metadata = get_project_metadata(self, old_name)
            old_display_name = metadata['project']['display_name']

            self.things.rename(old_display_name, new_display_name)
            self.files.rename(old_name, old_display_name, old_path, new_name, new_display_name, new_path)
            self.jekyll.rename(old_name, new_name, new_display_name)
            self.github.rename(old_name, new_name, new_path)
            self.pdf.rename(old_name, new_name)
            self.publish_project(new_name)

            self.logger.info(f"Successfully renamed project from {old_name} to {new_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to rename project: {e}")