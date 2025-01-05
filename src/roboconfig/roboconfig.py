import os
import re

import requests
from git import Repo

MESHDB_URL = "https://devdb.nycmesh.net"
CONFIGS_REPO_URL = "https://github.com/nycmeshnet/nycmesh-configs.git"


class RoboConfig:
    def __init__(self, local_dir="./var/nycmesh-configs"):
        self.local_dir = local_dir
        if not os.path.isdir(local_dir):
            repo_url = CONFIGS_REPO_URL
            self.repo = Repo.clone_from(repo_url, local_dir)
        else:
            self.repo = Repo(local_dir)

    def _get_user_input(self, prompt):
        return input(f"{prompt}: ")

    def _set_number(self, number):
        if number > 8000:
            # assign node number from install number
            res = requests.post(
                f"{MESHDB_URL}/api/v1/nn-assign/",
                json={
                    "install_number": number,
                    "password": os.environ["NN_ASSIGN_PSK"],
                },
            )
            if res.status_code not in [200, 201]:
                print(f"Error generating NN for {number}")
                print(res.text)
                exit(1)
            number = res.json()["network_number"]
        self.number = number

    def get_tag_options(self):
        version_pattern = r"v\d+\.\d+"
        # Add the tags that look like version numbers
        tag_commit_pairs = [
            (
                tag.name,
                tag.commit.committed_date,
            )
            for tag in self.repo.tags
            if re.match(version_pattern, tag.name)
        ]
        # Sort by commit date
        tag_commit_pairs.sort(key=lambda x: x[1])
        tag_commit_pairs.reverse()

        # Add the others
        tag_commit_pairs.extend(
            [
                (
                    tag.name,
                    tag.commit.committed_date,
                )
                for tag in self.repo.tags
                if not re.match(version_pattern, tag.name)
            ]
        )
        return [t[0] for t in tag_commit_pairs]

    def set_tag(self, tag_value):
        print(tag_value)
        if tag_value is None:
            # pick latest tag that matches a version number
            version_pattern = r"v\d+\.\d+"
            tag_commit_pairs = [
                (tag, tag.commit.committed_date)
                for tag in self.repo.tags
                if re.match(version_pattern, tag.name)
            ]
            tag_commit_pairs.sort(key=lambda x: x[1])
            self.chosen_tag = tag_commit_pairs[-1][0]
        else:
            for tag in self.repo.tags:
                if tag.name == tag_value:
                    self.chosen_tag = tag_value
                    break
        self.repo.git.checkout(self.chosen_tag)

    def get_template_options(self, device_value):
        return [f for f in os.listdir(f"{self.local_dir}/{device_value}")]

    def _set_template(self, device_value, template_name=None):
        if template_name is None or not os.path.isfile(
            f"{self.local_dir}/{device_value}/{template_name}"
        ):
            templates = [f for f in os.listdir(f"{self.local_dir}/{device_value}")]
            if len(templates) > 1:
                menu = ", ".join(templates)
                template_name = self._get_user_input(f"Template file: {menu}")
            else:
                template_name = templates[0]

        self.template_name = template_name
        with open(f"{self.local_dir}/{device_value}/{template_name}", "r") as fd:
            self.template = fd.read()

    def generate(self, device, template, param, number, output_path):
        self._set_number(number)
        self.chosen_tag = None
        self._set_template(device, template)

        # Extract explicitly passed parameters
        explicit_params = dict()
        for item in param:
            if ":" in item:
                l = item.split(":")
                explicit_params[l[0]] = ":".join(l[1:])
            else:
                print(f"Error: {item} is not a valid value for --param")
                exit(1)

        # Get all parameters
        pattern = r"\{\{(.*?)\}\}"
        matches = re.findall(pattern, self.template)
        for m in set(matches):
            if m in explicit_params.keys():
                param[m] = explicit_params[m]
            elif m in ["nodenumber", "network_number"]:
                param[m] = str(self.number)
            else:
                param[m] = self._get_user_input(m)

        # Evaluate template
        if output_path is None:
            cleaned_name = self.template_name.replace(".tmpl", "")
            output_path = f"./{self.number}-{cleaned_name}"
            print(f"Writing to {output_path}")
        self.output_path = output_path
        with open(output_path, "w") as fd:
            for k, v in param.items():
                # print(f"{k} = {v}")
                self.template = self.template.replace("{{" + k + "}}", v)
            fd.write(self.template)
