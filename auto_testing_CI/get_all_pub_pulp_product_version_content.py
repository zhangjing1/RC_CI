import sys
class GetAllPubPulpVersionContent():
	def __init__(self, file):
		file = open(file, 'r')
		e2e_version_content_string = file.readline()
		file.close()
		self.e2e_version_content_list = e2e_version_content_string.split('</tr>')
		self.pub_content = ""
		self.pulp_rpm_content = ""
		self.pulp_docker_content = ""
		self.all_pub_pulp_content = ""

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
		self.get_pub_content()
		self.get_pulp_rpm_content()
		self.get_pulp_docker_content()
		self.all_pub_pulp_content = self.pub_content + self.pulp_rpm_content + self.pulp_docker_content


if __name__ == "main":
	file = sys.argv[1]
	content = GetAllPubPulpVersionContent(file)
	content.get_all_pub_pulp_content()
	print content.all_pub_pulp_content