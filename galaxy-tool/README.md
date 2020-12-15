## Notes for setting up the SpyBOAT Galaxy tool

### Tool xml specs

- https://docs.galaxyproject.org/en/latest/dev/schema.html

### Local testing

- clone recent Galaxy repo from https://galaxyproject.org/admin/get-galaxy/
- set `sanitize_all_html:false` in `galaxy/config/galaxy.yml(.sample)`
- add tool to `galaxy/config/tool_conf.yml(.sample)`
- activate `galaxy/.venv` and pip3 install required Python dependencies
- copy/link local tool directory to `galaxy/tools/my_tool`
- `run.sh` to start local Galaxy at localhost:8080

### Toolshed(s)

Register at:

- https://testtoolshed.g2.bx.psu.edu/
- https://toolshed.g2.bx.psu.edu/


### commands

First put toolshed account details into `.planemo.yml`

- planemo lint [tool.xml]
- planemo shed_init --name spyboat
- planemo shed_create --shed_target testtoolshed
- planemo shed_update --shed_target toolshed

### Hosting repo

- https://github.com/galaxyproject/tools-iuc
- fork and create a dedicated branch

#### Guidelines

- https://galaxy-iuc-standards.readthedocs.io/en/latest/best_practices/tool_xml.html
