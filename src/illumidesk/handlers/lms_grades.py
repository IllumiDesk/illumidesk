import json
from illumidesk.grades import exceptions
from illumidesk.grades.senders import LTIGradeSender

from jupyterhub.handlers import BaseHandler

from tornado import web


class SendGradesHandler(BaseHandler):
    """
    Defines a POST method to process grades submission for a specific assignment within a course
    """

    async def post(self, course_id: str, assignment_name: str) -> None:
        self.log.debug(f'Data received to send grades-> course:{course_id}, assignment:{assignment_name}')

        lti_grade_sender = LTIGradeSender(course_id, assignment_name)
        try:
            lti_grade_sender.send_grades()
        except exceptions.GradesSenderCriticalError:
            raise web.HTTPError(400, 'There was an critical error, please check logs.')
        except exceptions.AssignmentWithoutGradesError:
            raise web.HTTPError(400, 'There are no grades yet to submit')
        except exceptions.GradesSenderMissingInfoError:
            raise web.HTTPError(400, 'Impossible to send grades. There are missing values, please check logs.')
        self.write(json.dumps({"success": True}))

