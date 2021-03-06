import json
import logging
import os
import re
from datetime import datetime

from nbgrader.api import Gradebook
from nbgrader.api import MissingEntry
from tornado.httpclient import AsyncHTTPClient

from illumidesk.apis.nbgrader_service import NbGraderServiceHelper
from illumidesk.authenticators.utils import LTIUtils
from illumidesk.lti13.auth import get_lms_access_token

from .exceptions import AssignmentWithoutGradesError
from .exceptions import GradesSenderCriticalError
from .exceptions import GradesSenderMissingInfoError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GradesBaseSender:
    """
    This class helps to send student grades from nbgrader database. Classes that inherit from this class must implement
    the send_grades() method.

    Args:
        course_id (str): Course id or name used in nbgrader
        assignment_name (str): Assignment name that needs to be processed and from which the grades are retrieved
    """

    def __init__(self, course_id: str, assignment_name: str):
        self.course_id = course_id
        self.assignment_name = assignment_name

        # get nbgrader connection string from env vars
        self.nbgrader_helper = NbGraderServiceHelper(course_id)

    async def send_grades(self):
        raise NotImplementedError()

    @property
    def grader_name(self):
        return f"grader-{self.course_id}"

    @property
    def gradebook_dir(self):
        return f"/home/{self.grader_name}/{self.course_id}"

    def _retrieve_grades_from_db(self):
        """Gets grades from the database"""
        out = []
        max_score = 0
        # Create the connection to the gradebook database
        with Gradebook(self.nbgrader_helper.db_url, course_id=self.course_id) as gb:
            try:
                # retrieve the assignment record
                assignment_row = gb.find_assignment(self.assignment_name)
                max_score = assignment_row.max_score
                submissions = gb.assignment_submissions(self.assignment_name)
                logger.info(
                    f"Found {len(submissions)} submissions for assignment: {self.assignment_name}"
                )
            except MissingEntry as e:
                logger.error("Assignment not found in database: %s" % e)
                raise GradesSenderMissingInfoError

            for submission in submissions:
                # retrieve the student to use the lms id
                student = gb.find_student(submission.student_id)
                out.append(
                    {"score": submission.score, "lms_user_id": student.lms_user_id}
                )
        logger.info(f"Grades found: {out}")
        logger.info("Maximum score for this assignment %s" % max_score)
        return max_score, out


class LTI13GradeSender(GradesBaseSender):
    """
    Creates a new class to help us to send grades saved in the nbgrader gradebook (sqlite) back to the LMS

    For simplify the submission we're using the lineitem_id (that is a url) obtained in authentication flow and it indicates us where send the scores
    So the assignment item in the database should contains the 'lms_lineitem_id' with something like /api/lti/courses/:course_id/line_items/:line_item_id

    Attrs:
        course_id: It's the course label obtained from lti claims
        assignment_name: the asignment name used on the nbgrader console
    """

    def __init__(self, course_id: str, assignment_name: str):
        super(LTI13GradeSender, self).__init__(course_id, assignment_name)

        self.private_key_path = os.environ.get("LTI13_PRIVATE_KEY")
        self.lms_token_url = os.environ.get("LTI13_TOKEN_URL")
        self.lms_client_id = os.environ.get("LTI13_CLIENT_ID")
        # retrieve the course entity from nbgrader-gradebook
        course = self.nbgrader_helper.get_course()
        self.course = course
        self.all_lineitems = []
        self.headers = {}

    def _find_next_url(self, link_header: str) -> str:
        """
        Extract the url value from link header value
        """
        # split the paths
        next_url = [n for n in link_header.split(",") if "next" in n]
        if next_url:
            # get only one
            next_url = next_url[0]
            logger.debug(f"There are more lineitems in: {next_url}")
            link_regex = re.compile(
                r"((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)",
                re.DOTALL,
            )  # noqa W605
            links = re.findall(link_regex, next_url)
            if links:
                return links[0][0]

    async def _get_lineitems_from_url(self, url: str) -> None:
        """
        Fetch the lineitems from specific url and add them to general list
        """
        items = []
        if not url:
            return
        client = AsyncHTTPClient()
        resp = await client.fetch(url, method="GET", headers=self.headers)
        items = json.loads(resp.body)
        if items:
            self.all_lineitems.extend(items)
            headers = resp.headers
            # check if there is more items/pages
            if "Link" in headers and "next" in headers["Link"]:
                next_url = self._find_next_url(headers["link"])
                await self._get_lineitems_from_url(next_url)

    async def _get_line_item_info_by_assignment_name(self) -> str:
        await self._get_lineitems_from_url(self.course.lms_lineitems_endpoint)
        if not self.all_lineitems:
            raise GradesSenderMissingInfoError(
                f"No line-items were detected for this course: {self.course_id}"
            )
        logger.debug(f"LineItems retrieved: {self.all_lineitems}")
        lineitem_matched = None
        for item in self.all_lineitems:
            item_label = item["label"]
            if (
                self.assignment_name.lower() == item_label.lower()
                or self.assignment_name.lower()
                == LTIUtils().normalize_string(item_label)
            ):
                lineitem_matched = item["id"]  # the id is the full url
                logger.debug(
                    f"There is a lineitem matched with the assignment {self.assignment_name}. {item}"
                )
                break
        if lineitem_matched is None:
            raise GradesSenderMissingInfoError(
                f"No lineitem matched with the assignment name: {self.assignment_name}"
            )

        client = AsyncHTTPClient()
        resp = await client.fetch(lineitem_matched, headers=self.headers)
        lineitem_info = json.loads(resp.body)
        logger.debug(f"Fetched lineitem info from lms {lineitem_info}")

        return lineitem_info

    async def _set_access_token_header(self):
        token = await get_lms_access_token(
            self.lms_token_url, self.private_key_path, self.lms_client_id
        )

        if "access_token" not in token:
            logger.info(f"response from {self.lms_token_url}: {token}")
            raise GradesSenderCriticalError('The "access_token" key is missing')

        # set all the headers to use in lms requests
        self.headers = {
            "Authorization": "{token_type} {access_token}".format(**token),
            "Content-Type": "application/vnd.ims.lis.v2.lineitem+json",
        }

    async def send_grades(self):
        max_score, nbgrader_grades = self._retrieve_grades_from_db()
        if not nbgrader_grades:
            raise AssignmentWithoutGradesError

        await self._set_access_token_header()

        lineitem_info = await self._get_line_item_info_by_assignment_name()
        score_maximum = lineitem_info["scoreMaximum"]
        client = AsyncHTTPClient()
        self.headers.update({"Content-Type": "application/vnd.ims.lis.v1.score+json"})
        for grade in nbgrader_grades:
            try:
                score = float(grade["score"])
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "userId": grade["lms_user_id"],
                    "scoreGiven": score,
                    "scoreMaximum": score_maximum,
                    "gradingProgress": "FullyGraded",
                    "activityProgress": "Completed",
                    "comment": "",
                }
                logger.info(f"data used to sent scores: {data}")

                url = lineitem_info["id"] + "/scores"
                logger.debug(f"URL for grades submission {url}")
                await client.fetch(
                    url, body=json.dumps(data), method="POST", headers=self.headers
                )
            except Exception as e:
                logger.error(
                    f"Something went wrong by sending grader for {grade['lms_user_id']}.{e}"
                )
