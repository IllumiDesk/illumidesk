# LTI 1.1
# Defined from https://www.imsglobal.org/specs/ltiv1p1p1/implementation-guide
# We define the user_id as required even though it is defined as recommended as it used as
# a fallback id for nbgrader's lms_user_id column.
LTI11_LAUNCH_PARAMS_REQUIRED = [
    'lti_message_type',
    'lti_version',
    'resource_link_id',
    'user_id',
]

LTI11_LAUNCH_PARAMS_RECOMMENDED = [
    'resource_link_title',
    'roles',
    'lis_person_name_given',
    'lis_person_name_family',
    'lis_person_name_full',
    'lis_person_contact_email_primary',
    'context_id',
    'context_title',
    'context_label',
    'launch_presentation_locale',
    'launch_presentation_document_target',
    'launch_presentation_width',
    'launch_presentation_height',
    'launch_presentation_return_url',
    'tool_consumer_info_product_family_code',
    'tool_consumer_info_version',
    'tool_consumer_instance_guid',
    'tool_consumer_instance_name',
    'tool_consumer_instance_contact_email',
]

LTI11_LAUNCH_PARAMS_OTIONAL = [
    'resource_link_description',
    'user_image',
    'role_scope_mentor',
    'context_type',
    'launch_presentation_css_url',
    'tool_consumer_instance_description',
    'tool_consumer_instance_url',
]

LTI11_LIS_OPTION = [
    'lis_outcome_service_url',
    'lis_result_sourcedid',
    'lis_person_sourcedid',
    'lis_course_offering_sourcedid',
    'lis_course_section_sourcedid',
]

# https://www.imsglobal.org/specs/ltiv1p1/implementation-guide
# Section 4.2
LTI11_OAUTH_ARGS = [
    'oauth_consumer_key',
    'oauth_signature_method',
    'oauth_timestamp',
    'oauth_nonce',
    'oauth_callback',
    'oauth_version',
    'oauth_signature',
]

LTI11_LAUNCH_PARAMS_REQUIRED = LTI11_LAUNCH_PARAMS_REQUIRED + LTI11_OAUTH_ARGS

LTI11_LAUNCH_PARAMS_ALL = LTI11_LAUNCH_PARAMS_REQUIRED + LTI11_LAUNCH_PARAMS_RECOMMENDED + LTI11_LAUNCH_PARAMS_OTIONAL

# LTI 1.3
# Required message claims
# http://www.imsglobal.org/spec/lti/v1p3/#required-message-claims
LTI13_REQUIRED_CLAIMS = {
    # these first two are set according to the spec
    'https://purl.imsglobal.org/spec/lti/claim/message_type': 'LtiResourceLinkRequest',
    'https://purl.imsglobal.org/spec/lti/claim/version': '1.3.0',
    # must not exceed 255 ascii chars
    'https://purl.imsglobal.org/spec/lti/claim/deployment_id': '',
    # should be the same as target_link_url
    'https://purl.imsglobal.org/spec/lti/claim/target_link_uri': '',
    # only resource_link's id is required
    'https://purl.imsglobal.org/spec/lti/claim/resource_link': {'id': '',},  # noqa: E231
    # roles is required, but can be empty.
    'https://purl.imsglobal.org/spec/lti/claim/roles': '',
}

# Optional message claims
# http://www.imsglobal.org/spec/lti/v1p3/#optional-message-claims
LTI13_OPTIONAL_CLAIMS = {
    'https://purl.imsglobal.org/spec/lti/claim/resource_link': {'description': '', 'title': '',},  # noqa: E231
    'https://purl.imsglobal.org/spec/lti/claim/context': {
        'id': '',
        'label': '',
        'title': '',
        'type': [
            'http://purl.imsglobal.org/vocab/lis/v2/course#CourseTemplate',
            'http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering',
            'http://purl.imsglobal.org/vocab/lis/v2/course#CourseSection',
            'http://purl.imsglobal.org/vocab/lis/v2/course#Group',
        ],
    },
    # user identity claims. sub is added to optional list to support anonymous
    # launches.
    'sub': '',
    'given_name': '',
    'family_name': '',
    'name': '',
    'email': '',
    'https://purl.imsglobal.org/spec/lti/claim/tool_platform': {
        'guid': '',
        'contact_email': '',
        'description': '',
        'url': '',
        'product_family_code': '',
        'version': '',
    },
    'https://purlimsglobal.org/spec/lti/claim/role_scope_mentor': [''],
    'https://purl.imsglobal.org/spec/lti/claim/launch_presentation': {
        # one of frame, iframe, window
        'document_target': '',
        'height': '',
        'width': '',
        'return_url': '',
        'locale': '',
    },
}

LTI13_LIS_CLAIMS = {
    'https://purl.imsglobal.org/spec/lti/claim/lis': {
        'course_offering_sourcedid': '',
        'course_section_sourcedid': '',
        'outcome_service_url': '',
        'person_sourcedid': '',
        'result_sourcedid': '',
    },
}

LTI13_ROLE_VOCABULARIES = {
    'SYSTEM_ROLES': {
        'CORE': {
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator',
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#None',
        },
        'NON_CORE': {
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#AccountAdmin',
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#Creator',
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#SysAdmin',
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#SysSupport',
            'http://purl.imsglobal.org/vocab/lis/v2/system/person#User',
        },
    },
    'INSTITUTION_ROLES': {
        'CORE': {
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Guest',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#None',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Other',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student',
        },
        'NON_CORE': {
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Alumni',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Observer',
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent',
        },
    },
    'CONTEXT_ROLES': {
        'CORE': {
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor',
        },
        'NON_CORE': {
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Manager',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Member',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Officer',
        },
        'CONTEXT_SUB_ROLES': {
            # administrator role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#Administrator',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#Developer',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#ExternalDeveloper',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#ExternalSupport',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#ExternalSystemAdministrator',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#Support',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator#SystemAdministrator',
            # content developer role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#ContentDeveloper',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#ContentExpert',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#ExternalContentExpert',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper#Librarian',
            # instructor role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#ExternalInstructor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#Grader',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#GuestInstructor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#Lecturer',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#PrimaryInstructor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#SecondaryInstructor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistant',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantGroup',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantOffering',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantSection',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantSectionAssociation',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor#TeachingAssistantTemplate',
            # Learner role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#ExternalLearner',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#GuestLearner',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#Instructor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#Learner',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner#NonCreditLearner',
            # Manager role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#AreaManager',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#CourseCoordinator',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#ExternalObserver',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#Manager',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Manager#Observer',
            # Member role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Member#Member',
            # Mentor role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Mentor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Advisor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Auditor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalAdvisor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalAuditor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalLearningFacilitator',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalMentor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalReviewer',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#ExternalTutor',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#LearningFacilitator',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Reviewer',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor#Tutor',
            # Officer role
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Chair',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Communications',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Secretary',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Treasurer',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Officer#Vice-Chair',
        },
    },
}

# https://www.imsglobal.org/spec/security/v1p0/#securing_web_services
LTI13_WEB_SERVICES_REQUIRED_CLAIMS = {
    'grant_type': '',
    'client_assertion_type': '',
    'client_assertion': '',
    'scope': '',
}

# https://www.imsglobal.org/spec/security/v1p0/#step-1-third-party-initiated-login
LTI13_THIRD_PARTY_INITIATED_LOGIN = {
    'iss': '',
    'login_hint': '',
    'target_link_uri': '',
}


# https://www.imsglobal.org/spec/security/v1p0/#step-2-authentication-request
LTI13_AUTHENTICATION_REQUEST = {
    'scope': '',
    'response_type': '',
    'client_id': '',
    'redirect_uri': '',
    'login_hint': '',
    'state': '',
    'reponse_mode': '',
    'nonce': '',
    'prompt': '',
}


# https://www.imsglobal.org/spec/security/v1p0/#step-2-authentication-request
LTI13_AUTHENTICATION_RESPONSE = {
    'state': '',
    'id_token': '',
}

# https://www.imsglobal.org/spec/security/v1p0/#id-token
LTI13_ID_TOKEN_CLAIMS = {
    'iss': '',
    'aud': '',
    'sub': '',
    'exp': '',
    'iat': '',
    'nonce': '',
    'azp': '',
}


# https://www.imsglobal.org/spec/security/v1p0/#h_key-set-url
LTI13_KEY_SET = {
    'e': '',
    'use': '',
    'alg': '',
    'kty': '',
    'n': '',
    'kid': '',
}
