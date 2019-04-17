# -*- coding: utf-8 -*-

__all__ = ['GeneralConfigurations']

class GeneralConfigurations:
  application_repo_url = 'https://github.com/fogbow/authentication-service.git'
  application_branch_under_test = 'develop'
  application = {
    'port': 8080
  }
  commands = {
    'run_application': "/usr/bin/mvn spring-boot:run"
  }
