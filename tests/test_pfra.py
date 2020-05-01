from unittest import TestCase
from ShellUtilities import Shell
from ShellUtilities.ShellCommandException import ShellCommandException
import os

class Test_pfra(TestCase):

    def __init__(self, *args, **kwargs):
        super(Test_pfra, self).__init__(*args, **kwargs)

        self.mock_service_name = "MockService"

        # Determine the current directory
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.root_dir = os.path.dirname(self.current_dir)

        # Determine the path to the shell script
        self.shell_script_path = os.path.join(self.root_dir, "src", "pfra.sh")
        self.promote_script_path = os.path.join(self.current_dir, "MockService", "promote.sh")
        self.demote_script_path = os.path.join(self.current_dir, "MockService", "demote.sh")

        # Set the environment variables as if we configured the resource agent using pcs
        self.env = os.environ
        self.env["OCF_ROOT"] = "/usr/lib/ocf/"
        self.env["OCF_RESKEY_service_name"] = self.mock_service_name
        self.env["OCF_RESKEY_promote_script"] = self.promote_script_path
        self.env["OCF_RESKEY_demote_script"] = self.demote_script_path

    def __is_service_running(self):

        shell_command = "systemctl status {0} | grep -E '^   Active: active \(running\)'".format(self.mock_service_name)
        try:
            shell_command_results = Shell.execute_shell_command(shell_command)
            return True
        except ShellCommandException:
            return False

    def __stop_mock_service(self):
        Shell.execute_shell_command("systemctl stop {0}".format(self.mock_service_name))

    def __start_mock_service(self):
        Shell.execute_shell_command("systemctl start {0}".format(self.mock_service_name))

    def test__usage__success__called_by_name(self):
        if self.__is_service_running():
            self.__stop_mock_service()

        try:
            shell_command = "bash {0} usage".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        except ShellCommandException as scex:
            self.assertEqual(2, scex.ExitCode)
            self.assertTrue("start|stop|monitor|meta-data|promote|demote" in scex.Stdout)
            self.assertEqual("", scex.Stderr)
            self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__usage__success__no_args_supplied(self):
        if self.__is_service_running():
            self.__stop_mock_service()

        try:
            shell_command = "bash {0}".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        except ShellCommandException as scex:
            self.assertEqual(2, scex.ExitCode)
            self.assertTrue("start|stop|monitor|meta-data|promote|demote" in scex.Stdout)
            self.assertEqual("", scex.Stderr)
            self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__start__success__not_started(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        shell_command = "bash {0} start".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Starting the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__start__success__already_started(self):

        if not self.__is_service_running():
            self.__start_mock_service()

        shell_command = "bash {0} start".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Starting the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Starting the service succeeded" in shell_command_results.Stderr)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__stop__success__not_started(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        shell_command = "bash {0} stop".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Stopping the service succeeded" in shell_command_results.Stderr)
        self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__stop__success__already_started(self):

        if not self.__is_service_running():
            self.__start_mock_service()

        shell_command = "bash {0} stop".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Stopping the service succeeded" in shell_command_results.Stderr)
        self.assertFalse(self.__is_service_running())

        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Stopping the service succeeded" in shell_command_results.Stderr)
        self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__monitor__success__not_running(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        tmp_env = self.env.copy()
        self.env["OCF_RESKEY_monitor_script"] = os.path.join(self.current_dir, "MockService", "monitor-not-running.sh")

        shell_command = "bash {0} monitor".format(self.shell_script_path)
        with self.assertRaises(ShellCommandException) as shell_command_exception_context:
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        shell_command_exception = shell_command_exception_context.exception
        self.assertEqual(7, shell_command_exception.ExitCode)

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__monitor__success__master(self):

        if not self.__is_service_running():
            self.__start_mock_service()

        tmp_env = self.env.copy()
        self.env["OCF_RESKEY_monitor_script"] = os.path.join(self.current_dir, "MockService", "monitor-master.sh")

        shell_command = "bash {0} monitor".format(self.shell_script_path)
        with self.assertRaises(ShellCommandException) as shell_command_exception_context:
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        shell_command_exception = shell_command_exception_context.exception
        self.assertEqual(8, shell_command_exception.ExitCode)

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__monitor__success__slave(self):

        if not self.__is_service_running():
            self.__start_mock_service()

        tmp_env = self.env.copy()
        self.env["OCF_RESKEY_monitor_script"] = os.path.join(self.current_dir, "MockService", "monitor-slave.sh")

        shell_command = "bash {0} monitor".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
        self.assertEqual(0, shell_command_results.ExitCode)

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__promote__success__service_running(self):

        if not self.__is_service_running():
            self.__start_mock_service()

        shell_command = "bash {0} promote".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)

        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Promoting to master" in shell_command_results.Stdout)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__promote__Failure__service_not_running(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        try:
            shell_command = "bash {0} promote".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
            raise Exception("The test case did not raise an exception as expected")
        except ShellCommandException as scex:

            self.assertEqual(1, scex.ExitCode)
            self.assertTrue("cannot be promoted because it is not running" in scex.Stderr)
            self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__promote__Failure__script_does_not_exist(self):
        if not self.__is_service_running():
            self.__start_mock_service()

        try:
            tmp_env = dict(self.env)
            tmp_env["OCF_RESKEY_promote_script"] = os.path.join('tmp', "this_does_not_exist.sh")

            shell_command = "bash {0} promote".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=tmp_env)
            raise Exception("The test case did not raise an exception as expected")
        except ShellCommandException as scex:

            self.assertEqual(1, scex.ExitCode)
            self.assertTrue("promotion script does not exist" in scex.Stderr)
            self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

        self.env["OCF_RESKEY_promote_script"] = self.promote_script_path

    def test__demote__success__service_running(self):

        if not self.__is_service_running():
            self.__start_mock_service()

        shell_command = "bash {0} demote".format(self.shell_script_path)
        shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)

        self.assertEqual(0, shell_command_results.ExitCode)
        self.assertTrue("Demoting to slave" in shell_command_results.Stdout)
        self.assertTrue(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__demote__Failure__service_not_running(self):

        if self.__is_service_running():
            self.__stop_mock_service()

        try:
            shell_command = "bash {0} demote".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
            raise Exception("The test case did not raise an exception as expected")
        except ShellCommandException as scex:

            self.assertEqual(1, scex.ExitCode)
            self.assertTrue("cannot be demoted because it is not running" in scex.Stderr)
            self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

    def test__demote__Failure__script_does_not_exist(self):
        if self.__is_service_running():
            self.__stop_mock_service()

        try:
            tmp_env = self.env.copy()
            self.env["OCF_RESKEY_promote_script"] = os.path.join('tmp', "this_does_not_exist.sh")

            shell_command = "bash {0} demote".format(self.shell_script_path)
            shell_command_results = Shell.execute_shell_command(shell_command, env=self.env)
            raise Exception("The test case did not raise an exception as expected")
        except ShellCommandException as scex:

            self.assertEqual(1, scex.ExitCode)
            self.assertTrue("cannot be demoted because it is not running" in scex.Stderr)
            self.assertFalse(self.__is_service_running())

        if self.__is_service_running():
            self.__stop_mock_service()

        self.env["OCF_RESKEY_demote_script"] = self.demote_script_path
