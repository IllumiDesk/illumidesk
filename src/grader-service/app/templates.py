#  (C) Copyright IllumiDesk, LLC, 2020.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
#  the License. You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
#  specific language governing permissions and limitations under the License.

NBGRADER_HOME_CONFIG_TEMPLATE = """
c = get_config()

c.CourseDirectory.root = '/home/{grader_name}/{course_id}'
c.ClearSolutions.code_stub = {{
    "python": "# your code here\\nraise NotImplementedError",
    "javascript": "// your code here\\nthrow new Error();",
    "julia": "# your code here\\nthrow(ErrorException())"
}}
c.CourseDirectory.db_url = '{db_url}'
"""


NBGRADER_COURSE_CONFIG_TEMPLATE = """
c = get_config()

c.CourseDirectory.course_id = '{course_id}'
c.IncludeHeaderFooter.header = 'source/header.ipynb'
c.IncludeHeaderFooter.footer = 'source/footer.ipynb'
"""
