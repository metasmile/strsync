#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plistlib
import subprocess
import os.path
import distutils.spawn

class XCodeProjectReadException(Exception):
    pass


class XCodeConfiguration(object):
    @classmethod
    def from_list(cls, configurations_dict, objects_dict):
        configurations = {}
        for configuration_id in configurations_dict['buildConfigurations']:
            configuration = cls(objects_dict[configuration_id])
            configurations[configuration.name] = configuration

        return configurations

    def __init__(self, configuration_dict=None):
        self.name = ''
        self.build_settings = {}

        if configuration_dict:
            self.set_from_dict(configuration_dict)

    def set_from_dict(self, configuration_dict):
        self.name = configuration_dict['name']
        self.build_settings = configuration_dict['buildSettings']


class XCodeTarget(object):
    def __init__(self, target_dict=None, objects_dict=None):
        self.name = ''
        self.product_name = ''
        self.configurations = {}

        if target_dict and objects_dict:
            self.set_from_dict(target_dict, objects_dict)

    def set_from_dict(self, target_dict, objects_dict):
        self.name = target_dict['name']
        self.product_name = target_dict['productName']

        configurations_dict = objects_dict[
            target_dict['buildConfigurationList']
        ]
        self.configurations = XCodeConfiguration.from_list(
            configurations_dict, objects_dict
        )

    def get_build_setting(self, setting, configuration='Release'):
        build_settings = self.configurations.get(
            configuration, XCodeConfiguration()
        ).build_settings

        return build_settings.get(setting, None)


class XCodeProject(object):
    def __init__(self, project_file_path=None):
        self.objects = {}
        self.configurations = {}
        self.targets = {}

        if project_file_path:
            self.set_from_project_file(project_file_path)

    def set_from_project_file(self, project_file_path):
        pbxproj_file_path = os.path.join(project_file_path, 'project.pbxproj')
        if not os.path.exists(pbxproj_file_path):
            raise XCodeProjectReadException(
                'Could not find the XCode project file: %s does not exist' %
                pbxproj_file_path
            )

        if not 'plutil' in distutils.spawn.find_executable("plutil"):
            raise XCodeProjectReadException(
                'Could not find a command "plutil"'
            )

        arguments = 'plutil -convert xml1 -o -'.split(' ')
        arguments.append(pbxproj_file_path)
        process = subprocess.Popen(arguments, stdout=subprocess.PIPE)
        stdoutdata = process.communicate()[0]

        if process.returncode != 0:
            raise XCodeProjectReadException(
                'Could not read the project file: %s' % stdoutdata
            )

        objects_dict = plistlib.readPlistFromString(stdoutdata)['objects']
        self.objects = objects_dict

        for item_dict in objects_dict.itervalues():
            isa = item_dict['isa']

            if isa == 'PBXNativeTarget':
                target = XCodeTarget(item_dict, objects_dict)
                self.targets[target.name] = target

            if isa in ('PBXProject'):
                configurations_dict = objects_dict[
                    item_dict['buildConfigurationList']
                ]
                self.configurations = XCodeConfiguration.from_list(
                    configurations_dict, objects_dict
                )

    def get_build_setting(self, setting, configuration='Release', target=None):
        build_settings = self.configurations.get(
            configuration, XCodeConfiguration()
        ).build_settings

        value = build_settings.get(setting, None)

        if not target or value:
            return value
        else:
            target = self.targets.get(target, XCodeTarget())

            return target.get_build_setting(setting, configuration)


def main():
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)

    if len(sys.argv) < 2:
        logging.error('Please specify an XCode project file')
        logging.error('usage: %s app.xcodeproj', sys.argv[0])
        return 1

    project_file_path = sys.argv[1]

    logging.info('Scanning file %s', project_file_path)

    try:
        project = XCodeProject(project_file_path)
    except XCodeProjectReadException, exc:
        logging.error(exc)
        return 2

    logging.debug('Project settings:')
    for configuration in project.configurations.itervalues():
        logging.debug('  * %s:', configuration.name)
        for key, value in configuration.build_settings.iteritems():
            logging.debug('    > %s = %s', key, value)

    for target in project.targets.itervalues():
        logging.debug('Target %s (%s):', target.name, target.product_name)
        for configuration in target.configurations.itervalues():
            logging.debug('  * %s:', configuration.name)
            for key, value in configuration.build_settings.iteritems():
                logging.debug('    > %s = %s', key, value)

    first_target_name = project.targets.iterkeys().next()
    logging.debug(
        '%s Info.plist file: %s',
        first_target_name,
        project.get_build_setting('INFOPLIST_FILE', target=first_target_name)
    )

    logging.debug('Main SDK: %s', project.get_build_setting('SDKROOT'))

    return 0


if __name__ == '__main__':
    import logging
    import sys

    sys.exit(main())
