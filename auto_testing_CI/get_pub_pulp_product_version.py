#/bin/env python
import sys
class GetPubAndPulpVersion():
	def __init__(self, file, build_name):
		file = open(file, 'r')
		e2e_version_content_string = file.readline()
		file.close()
		self.e2e_version_content_list = e2e_version_content_string.split('</tr>')
		self.pub_version = ""
		self.pub_build = ""
		self.pub_rcm_pa_tool_build = ""
		self.pulp_rpm_build = ""
		self.pulp_for_rpm= ""
		self.pulp_cdn_distributor_plugins_build = ""
		self.pulp_docker_build = ""
		self.pulp_for_docker = ""
		self.build_name = build_name
		self.build_name_list = {}

	def get_pub_build_name(self):
		self.pub_build = self.e2e_version_content_list[3].split('</td>')[1].split("</p>")[0].split('>')[2].split('pub')[1].split("-1.el")[0]
		self.build_name_list['pub'] = 'pub-hub' + self.pub_build

	def get_pulp_build_name_for_pulprpm(self):
		self.pulp_build_for_rpm = self.e2e_version_content_list[4].split("</td>")[1].split("</p>")[0].split(">")[2].split(':')[1]
		self.build_name_list['pulp_for_rpm'] = 'pulp-server-' + self.pulp_build_for_rpm.strip()

	def get_pulp_rpm_build_name(self):
		self.pulp_rpm_build = self.e2e_version_content_list[4].split("</td>")[1].split("</p>")[1].split('>')[1].split(':')[1]
		self.build_name_list['pulp-rpm-plugins'] = "pulp-rpm-plugins-" + self.pulp_rpm_build.strip()

	def get_pulp_cdn_distributor_plugins_build(self):
		self.pulp_cdn_distributor_plugins_build = self.e2e_version_content_list[4].split("</td>")[1].split("</p>")[2].split('>')[1].split(":")[1]
		self.build_name_list['pulp-cdn-distributor-plugins'] = "pulp-cdn-distributor-plugins-" + self.pulp_cdn_distributor_plugins_build.strip()

	def get_pulp_build_name_for_pulpdocker(self):
		self.pulp_for_docker = self.e2e_version_content_list[5].split('</td>')[1].split('</p>')[0].split('p>')[1].split(':')[1]
		self.build_name_list['pulp_for_docker'] = "pulp-server-" + self.pulp_for_docker.strip()

	def get_pulp_docker_build_name(self):
		self.pulp_docker_build = self.e2e_version_content_list[5].split('</td>')[1].split('</p>')[1].split('<p>')[1].split(":")[1]
		self.build_name_list['pulp-docker-plugins'] = 'pulp-docker-plugins-' + self.pulp_docker_build.strip()

	def get_builds_name_list(self):
		# get pub info
		self.get_pub_build_name()
		# get pulp rpm info
		self.get_pulp_build_name_for_pulprpm()
		self.get_pulp_rpm_build_name()
		self.get_pulp_cdn_distributor_plugins_build()
		# get pulp docker info
		self.get_pulp_build_name_for_pulpdocker()
		self.get_pulp_docker_build_name()
		return self.build_name_list[self.build_name]

if __name__=="__main__":
	file = sys.argv[1]
	build_name = sys.argv[2]
	get_pub_pulp_version = GetPubAndPulpVersion(file, build_name)
	print get_pub_pulp_version.get_builds_name_list()