import yaml
import mdx_math
import abc
import sys
import re
import os.path
from os import listdir
from kordac import Kordac
from .check_converter_required_files import check_required_files


class BaseLoader():
    """Base loader class for individual loaders"""

    def __init__(self, BASE_PATH='', load_log=[]):
        if load_log:
            self.load_log = load_log
        else:
            self.load_log = list(load_log)
        self.BASE_PATH = BASE_PATH
        self.setup_md_to_html_converter()

    def setup_md_to_html_converter(self):
        """Create Kordac converter with custom processors, html templates,
        and extensions.
        """
        templates = self.load_template_files()
        extensions = [
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.sane_lists',
            'markdown.extensions.tables',
            mdx_math.MathExtension(enable_dollar_delimiter=True)
        ]
        self.converter = Kordac(html_templates=templates, extensions=extensions)
        custom_processors = self.converter.processor_defaults()
        custom_processors.add('remove-title')
        self.converter.update_processors(custom_processors)

    def convert_md_file(self, md_file_path):
        """Returns the Kordac object for a given Markdown file

        Args:
            file_path: location of md file to convert

        Returns:
            Kordac result object
        """
        content = open(md_file_path, encoding='UTF-8').read()
        result = self.converter.convert(content)
        check_required_files(result.required_files)
        return result

    def log(self, log_message, indent_amount=0):
        """Adds the log message to the load log with the specified indent"""
        self.load_log.append((log_message, indent_amount))

    def print_load_log(self):
        """Output log messages from loader to console"""
        for (log, indent_amount) in self.load_log:
            indent = '  ' * indent_amount
            sys.stdout.write('{indent}{text}\n'.format(indent=indent, text=log))
        sys.stdout.write('\n')
        self.load_log = []

    def load_yaml_file(self, yaml_file_path):
        """Loads and reads yaml file

        Args:
            file_path: location of yaml file to read

        Returns:
             Either list or string, depending on structure of given yaml file
        """
        yaml_file = open(yaml_file_path, encoding='UTF-8').read()
        return yaml.load(yaml_file)

    def load_template_files(self):
        """Loads custom HTMl templates for converter

        Returns:
           templates: dictionary of html templates
        """
        templates = dict()
        template_path = os.path.join(
            os.path.dirname(__file__),
            'custom_converter_templates/'
        )
        for file in listdir(template_path):
            template_file = re.search(r'(.*?).html$', file)
            if template_file:
                template_name = template_file.groups()[0]
                templates[template_name] = open(template_path + file).read()
        return templates

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError('subclass does not implement this method')