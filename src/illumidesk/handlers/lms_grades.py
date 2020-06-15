import json

from illumidesk.authenticators.authenticator import LTI11Authenticator
from illumidesk.grades import exceptions
from illumidesk.grades.senders import LTIGradeSender, LTI13GradeSender

from jupyterhub.handlers import BaseHandler

from tornado import web


class SendGradesHandler(BaseHandler):
    """
    Defines a POST method to process grades submission for a specific assignment within a course
    """
    @property
    def authenticator_class(self):
        return self.settings.get('authenticator_class', None)

    async def post(self, course_id: str, assignment_name: str) -> None:
        self.log.debug(f'Data received to send grades-> course:{course_id}, assignment:{assignment_name}')

        lti_grade_sender = None

        # check lti version by the authenticator setting
        if self.authenticator_class == LTI11Authenticator:
            lti_grade_sender = LTIGradeSender(course_id, assignment_name)
        else:
            lti_grade_sender = LTI13GradeSender(course_id, assignment_name)

        try:
            await lti_grade_sender.send_grades()
        except exceptions.GradesSenderCriticalError:
            raise web.HTTPError(400, 'There was an critical error, please check logs.')
        except exceptions.AssignmentWithoutGradesError:
            raise web.HTTPError(400, 'There are no grades yet to submit')
        except exceptions.GradesSenderMissingInfoError:
            raise web.HTTPError(400, 'Impossible to send grades. There are missing values, please check logs.')
        self.write(json.dumps({"success": True}))

