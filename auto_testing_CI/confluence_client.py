import sys
import ci3_error
from confluence import Api
import confluence_rest_api_client
class ConfluenceClient():
	def __init__(self, username, password, title, space, content, parent_page):
		self.wiki_url = "https://docs.engineering.redhat.com"
		self.username = username
		self.password = password
		self.api = Api(self.wiki_url, self.username, self.password)
		self.page_name = title
		self.general_content = content
		self.space = space
		self.parent_page = parent_page
		self.content = ""
		self.page_all_info = {}

	def create_update_page(self):
		self.get_page_content()
		if self.content.find("it does not exist.") > 0 or self.content.find("QE") < 0 :
			print "==== Will add page ==="
			print "==== The page title: ", self.page_name
			self.api.addpage(self.page_name, self.space, self.general_content, parentpage=self.parent_page)
		else:
			self.get_page_all()
			print "==== Will update page ==="
			print "==== The page title: ", self.page_name
			update_confluence_client = confluence_rest_api_client.ConfluenceClientForUpdatePage(self.space, self.page_name, self.wiki_url, self.username, self.password)
			update_confluence_client.update_page(self.page_all_info, self.general_content)

	def get_page_content(self):
		try:
			self.content = self.api.getpagecontent(self.page_name, self.space)
		except Exception, error:
			self.content = str(error)

	def get_page_all(self):
		try:
			self.page_all_info = self.api.getpage(self.page_name, self.space)
		except Exception, error:
			print str(error)




if __name__ == "__main__":
	get_page = "false"
	create_update_page = "false"
	if len(sys.argv) == 5:
		get_page = "true"
	elif len(sys.argv) == 7:
		create_update_page = "true"
	else:
		raise ci3_error.ConfulenceClientInputError()

	username = sys.argv[1]
	password = sys.argv[2]
	title = sys.argv[3]
	space = sys.argv[4]
	if get_page == "true":
		confulence_client = ConfluenceClient(username, password, title, space, "", "")
		confulence_client.get_page_content()
	if create_update_page == "true":
		content = sys.argv[5]
		parentpage = sys.argv[6]
		confulence_client =  ConfluenceClient(username, password, title, space, content, parentpage)
		confulence_client.create_update_page()
