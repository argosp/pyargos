import argparse
import jinja2
import json
import os
import sys
import pydoc

parser = argparse.ArgumentParser()
parser.add_argument("--expConf", dest="expConf" , help="The Experiment configuration JSON", default='experimentConfiguration.json')
parser.add_argument("--reportName", dest="reportName" , help="The report name", required=True)
args = parser.parse_args()

with open(args.expConf, 'r') as confFile:
    config = json.load(confFile)

templatesPath = os.path.join(config['experimentPath'], 'reports', 'templates')

sys.path.insert(1, config['experimentPath'])
report_obj = pydoc.locate('reports.templates.report{Name}.{Name}'.format(Name=args.reportName))

latex_jinja_env = jinja2.Environment(
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(templatesPath)
)

report = report_obj(args.expConf, latex_jinja_env)
report.makeReport()


#template = latex_jinja_env.get_template('hello_world.tex')
#rendered_tex = template.render(text='Hello World')