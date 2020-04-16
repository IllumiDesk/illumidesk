NB_GRADER_CONFIG_TEMPLATE = """
c = get_config()

c.CourseDirectory.root = '/home/{grader_name}/{course_id}'
c.CourseDirectory.course_id = '{course_id}'
"""
