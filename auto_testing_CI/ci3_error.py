class Error():
	"""Base class for exceptions in this module."""
	pass

class ConfulenceClientInputError(Error):
    """
    Exception raised for input errors of confluence_client.py
    """

    def __init__(self):
        message = '''
        Input Error, please check your inputs
        To get page content/summary: username password space title
        To create/update page: username, password, space, title, content, parent_page
        '''
        print message

class GetAllPubPulpVersionContentInputError(Error):
	"""
	Exception raised for input errors of get_all_pub_pulp_content_version_content.py
	"""
	def __init__(self):
		message = '''
		Input Error, please check your inputs
		To get the page content, username and password are both needed
		'''
		print message

class CollectAllReportsAndAddToConfluenceInputError(Error):
	"""
	Exception railsed for input errors of collect_all_reports_and_add_to_confluence.py
	"""
	def __init__(self):
		message = '''
		Input Error, please check your inputs
		To collect all reports and add them to the confluence page: username, password, et_build_version, title, space, content, parent_page
		'''
		print message