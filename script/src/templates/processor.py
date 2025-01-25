from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader
from script.src.config import Config
from script.src.constants import Status
from script.src.utils import (
    get_project_content,
    get_project_metadata,
    get_project_path,
    is_public_github_repo,
)


class TemplateProcessor:
    def __init__(self, config: Config, content_type):
        self.config = config
        self.content_type = content_type
        current_dir = Path(__file__).parent
        self.env = Environment(
            loader=FileSystemLoader(current_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def get_media_files(self, name, extensions):
        """Get all media files of specified type and extensions."""
        project_dir = get_project_path(self, name)
        media_path = project_dir / 'media'
        files = []
        for ext in extensions:
            files.extend(list(media_path.rglob(ext)))
        return files

    def process_template(self, name: str, template_name: str, context: Dict={}):
        """Process template with given context."""
        context = context | self.process_project_metadata(name)
        if self.content_type:
            context['content'] = get_project_content(self, name, self.content_type)
        template = self.env.get_template(template_name)
        return template.render(context)
        
    def process_project_metadata(self, name: str) -> Dict:
        metadata = get_project_metadata(self, name)
        
        project = metadata['project']

        if (project['status'] == Status.COMPLETE):
            project['website'] = f"{self.config.website_domain}/{name}"
        if is_public_github_repo(self, name):
            project['github'] = f"{self.config.github_url_path}/{name}"

        specs = metadata['physical_specifications']
            
        dimensions = f"{specs['dimensions']['width']}{specs['dimensions']['unit']} w x {specs['dimensions']['height']}{specs['dimensions']['unit']} h x {specs['dimensions']['depth']}{specs['dimensions']['unit']} d"
        weight = f"{specs['weight']['value']} {specs['weight']['unit']}"
        
        materials = specs['materials']['primary']
        consumables = specs['materials']['consumables']

        materials = ", ".join(materials)
        consumables = ", ".join(materials)

        reqs = metadata['technical_requirements']

        lighting = reqs['lighting']
        mounting = reqs['mounting']
        temperature_range = reqs['environmental']['temperature_range']
        humidity_range = reqs['environmental']['humidity_range']
        ventilation_needs = reqs['environmental']['ventilation_needs']

        ex = metadata['exhibition']

        setup_instructions = ex['setup']['instructions']
        setup_time = ex['setup']['time_required']
        setup_people = ex['setup']['people_required']
        setup_tools = ", ".join(ex['setup']['tools_required'])

        maintenance_supplies = ", ".join(ex['maintenance']['supplies_needed'])
        maintenance_instructions = ex['maintenance']['tasks']

        # Prepare template data
        return {
            'project': project,
            'dimensions': dimensions,
            'weight': weight,
            'materials': materials,
            'consumables': consumables,
            'lighting': lighting,
            'mounting': mounting,
            'temperature_range': temperature_range,
            'humidity_range': humidity_range,
            'ventilation_needs': ventilation_needs,
            'setup_instructions': setup_instructions,
            'setup_time': setup_time,
            'setup_tools': setup_tools,
            'setup_people': setup_people,
            'maintenance_supplies': maintenance_supplies,
            'maintenance_instructions': maintenance_instructions,
        }
