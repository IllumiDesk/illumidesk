NB_GRADER_CONFIG_TEMPLATE = """
c = get_config()

c.CourseDirectory.root = '/home/{grader_name}/{course_id}'
c.CourseDirectory.course_id = '{course_id}'
c.ClearSolutions.code_stub = {{
    "python": "# your code here\\nraise NotImplementedError",
    "javascript": "// your code here\\nthrow new Error();",
    "julia": "# your code here\\nthrow(ErrorException())"
}}
"""
