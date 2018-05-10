import sys
import confluence_client
import ci3_error
class GetAllPubPulpVersionContent():
	def __init__(self, username, password):
		version_page_name="Version of Applications in E2E"
		version_page_space="~lzhuang"
		self.confluence_api_client = confluence_client.ConfluenceClient(username, password, version_page_name, version_page_space, "", "")
		self.versions_content = ""
		self.e2e_version_content_list = ""
		self.pub_content = ""
		self.pulp_rpm_content = ""
		self.pulp_docker_content = ""
		self.all_pub_pulp_content = ""

	def get_versions_content(self):
		self.confluence_api_client.get_page_content()
		self.versions_content = self.confluence_api_client.content

	def get_version_content_split(self):
		self.e2e_version_content_list = self.versions_content.split('</tr>')

	def get_pub_content(self):
		pub_version_content = self.e2e_version_content_list[3].split("</td>")[1].replace("td", 'p').replace("<tr>", "").replace("<p><p>", "<p>")
		self.pub_content = "<p>" + "Pub:" + "</p>" + pub_version_content

	def get_pulp_rpm_content(self):
		pulp_rpm_version_content = self.e2e_version_content_list[4].split("</td>")[1].replace("td", 'p').replace("<tr>", "").replace("<p><p>", "<p>")
		self.pulp_rpm_content = "<p>" + "Pulp RPM:" + "</p>" + pulp_rpm_version_content

	def get_pulp_docker_content(self):
		pulp_docker_version_content = self.e2e_version_content_list[5].split("</td>")[1].replace("td", 'p').replace("<tr>", "").replace("<p><p>", "<p>")
		self.pulp_docker_content = "<p>" + "Pulp Docker:" + "</p>" + pulp_docker_version_content

	def get_all_pub_pulp_content(self):
		self.get_versions_content()
		self.get_version_content_split()
		self.get_pub_content()
		self.get_pulp_rpm_content()
		self.get_pulp_docker_content()
		self.all_pub_pulp_content = self.pub_content + self.pulp_rpm_content + self.pulp_docker_content


if __name__ == "__main__":
	if len(sys.argv) != 3:
		raise ci3_error.GetAllPubPulpVersionContentInputError()
	else:
		username = sys.argv[1]
		password = sys.argv[2]
	content = GetAllPubPulpVersionContent(username, password)
	content.get_all_pub_pulp_content()