#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Linux preprocess plug-ins."""

from __future__ import unicode_literals

import unittest

from dfvfs.helpers import fake_file_system_builder
from dfvfs.path import fake_path_spec

from plaso.preprocessors import linux

from tests.preprocessors import test_lib


class LinuxHostnamePluginTest(test_lib.ArtifactPreprocessorPluginTestCase):
  """Tests for the Linux hostname plugin."""

  _FILE_DATA = b'plaso.kiddaland.net\n'

  def testParseFileData(self):
    """Tests the _ParseFileData function."""
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()
    file_system_builder.AddFile('/etc/hostname', self._FILE_DATA)

    mount_point = fake_path_spec.FakePathSpec(location='/')

    plugin = linux.LinuxHostnamePlugin()
    knowledge_base = self._RunPreprocessorPluginOnFileSystem(
        file_system_builder.file_system, mount_point, plugin)

    self.assertEqual(knowledge_base.hostname, 'plaso.kiddaland.net')


class LinuxTimeZonePluginTest(test_lib.ArtifactPreprocessorPluginTestCase):
  """Tests for the Linux time zone plugin."""

  def testParseFileEntry(self):
    """Tests the _ParseFileEntry function."""
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()
    file_system_builder.AddSymbolicLink(
        '/etc/localtime', '/usr/share/zoneinfo/Europe/Zurich')

    mount_point = fake_path_spec.FakePathSpec(location='/')

    plugin = linux.LinuxTimeZonePlugin()
    knowledge_base = self._RunPreprocessorPluginOnFileSystem(
        file_system_builder.file_system, mount_point, plugin)

    self.assertEqual(knowledge_base.timezone.zone, 'Europe/Zurich')


class LinuxUserAccountsPluginTest(test_lib.ArtifactPreprocessorPluginTestCase):
  """Tests for the Linux user accounts plugin."""

  _FILE_DATA = (
      b'root:x:0:0:root:/root:/bin/bash\n'
      b'bin:x:1:1:bin:/bin:/sbin/nologin\n'
      b'daemon:x:2:2:daemon:/sbin:/sbin/nologin\n'
      b'adm:x:3:4:adm:/var/adm:/sbin/nologin\n'
      b'lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin\n'
      b'sync:x:5:0:sync:/sbin:/bin/sync\n'
      b'shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown\n'
      b'halt:x:7:0:halt:/sbin:/sbin/halt\n'
      b'mail:x:8:12:mail:/var/spool/mail:/sbin/nologin\n'
      b'operator:x:11:0:operator:/root:/sbin/nologin\n'
      b'games:x:12:100:games:/usr/games:/sbin/nologin\n'
      b'ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin\n'
      b'nobody:x:99:99:Nobody:/:/sbin/nologin\n')

  def testParseFileData(self):
    """Tests the _ParseFileData function."""
    file_system_builder = fake_file_system_builder.FakeFileSystemBuilder()
    file_system_builder.AddFile('/etc/passwd', self._FILE_DATA)

    mount_point = fake_path_spec.FakePathSpec(location='/')

    plugin = linux.LinuxUserAccountsPlugin()
    knowledge_base = self._RunPreprocessorPluginOnFileSystem(
        file_system_builder.file_system, mount_point, plugin)

    users = sorted(
        knowledge_base.user_accounts,
        key=lambda user_account: user_account.identifier)
    self.assertEqual(len(users), 13)

    user_account = users[4]

    self.assertEqual(user_account.identifier, '14')
    self.assertEqual(user_account.group_identifier, '50')
    self.assertEqual(user_account.user_directory, '/var/ftp')
    self.assertEqual(user_account.username, 'ftp')
    self.assertEqual(user_account.shell, '/sbin/nologin')


if __name__ == '__main__':
  unittest.main()
