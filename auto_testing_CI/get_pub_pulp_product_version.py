#/bin/env python
import sys
class GetPubAndPulpVersion():
	def __init__(self, file, build_name):
		file = open(file, 'r')
		self.e2e_version_content_list = file.readlines()
		file.close()
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
		self.pub_build = self.e2e_version_content_list[0].split(':')[1]
		self.pub_build = '-'.join(self.pub_build.split('-')[1:]).strip()
		self.build_name_list['pub'] = 'pub-hub' + self.pub_build

	def get_pulp_build_name_for_pulprpm(self):
		self.pulp_build_for_rpm = self.e2e_version_content_list[1].split(':')[1].strip()
		self.build_name_list['pulp_for_rpm'] = 'pulp-server-' + self.pulp_build_for_rpm

	def get_pulp_rpm_build_name(self):
		self.pulp_rpm_build = self.e2e_version_content_list[2].split(':')[1].strip()
		self.build_name_list['pulp-rpm-plugins'] = "pulp-rpm-plugins-" + self.pulp_rpm_build

	def get_pulp_build_name_for_pulpdocker(self):
		self.pulp_for_docker = self.e2e_version_content_list[3].split(':')[1].strip()
		self.build_name_list['pulp_for_docker'] = "pulp-server-" + self.pulp_for_docker

	def get_pulp_docker_build_name(self):
		self.pulp_docker_build = self.e2e_version_content_list[5].split(':')[1].strip()
		self.build_name_list['pulp-docker-plugins'] = 'pulp-docker-plugins-' + self.pulp_docker_build

	def get_builds_name_list(self):
		# get pub info
		self.get_pub_build_name()
		# get pulp rpm info
		self.get_pulp_build_name_for_pulprpm()
		self.get_pulp_rpm_build_name()
		# get pulp docker info
		self.get_pulp_build_name_for_pulpdocker()
		self.get_pulp_docker_build_name()
		return self.build_name_list[self.build_name]

if __name__=="__main__":
	file = sys.argv[1]
	build_name = sys.argv[2]
	get_pub_pulp_version = GetPubAndPulpVersion(file, build_name)
	print get_pub_pulp_version.get_builds_name_list()
